import sys
import os
import struct

class DataScanner:
	def __init__(self, data):
		self.offset = 0
		self.data = data

	def advance(self, length):
		self.offset += length

	def read(self, length):
		output = self.peek(length)
		self.advance(length)
		return output

	def peek(self, length):
		return self.data[self.offset:(self.offset + length)]

	def readString(self):
		length = int.from_bytes(self.peek(4), byteorder="little")
		length += (4 - length) % 4
		return self.read(length + 4)

	def rest(self):
		return self.data[self.offset:]

def readString(str):
	length = int.from_bytes(str[0:4], byteorder="little")
	return str[4:(4+length)].decode("utf-8")

class FontFile:
	def __init__(self, data, filename, emptyAtlasPoint=None):
		stringLength = int.from_bytes(data[(4 * 15):(4 * 16)], byteorder="little")
		if stringLength in range(4, 26): # Assumes filenames are between 4 and 25 chars
			print(f"Detected {filename} as coming from TextMesh Pro")
			self.type = "TMP"
			self._fromAssetCreator(data, filename, emptyAtlasPoint)
		else:
			stringLength = int.from_bytes(data[(4*12):(4*13)], byteorder="little")
			if stringLength == 1:
				print(f"Detected {filename} as coming from a newer Higurashi game")
				self.type = "Hima"
			else:
				print(f"Detected {filename} as coming from an older Higurashi game")
				self.type = "Oni"
			self._fromGame(data, filename, emptyAtlasPoint)
		self.filename = readString(self.Filename)

	def _readArray(self, data, itemLength, emptyAtlasPoint):
		self.Array = data.read(4)
		length = int.from_bytes(self.Array, byteorder="little")
		atlasWidth = struct.unpack("<f", self.AtlasWidth)[0]
		atlasHeight = struct.unpack("<f", self.AtlasHeight)[0]
		cr = None
		lf = False
		for _ in range(length):
			info = bytearray(data.read(4 * 8))
			unicodeScalar = int.from_bytes(info[0:4], byteorder="little")
			if unicodeScalar == 0x0A:
				lf = True
			if unicodeScalar == 0x0D:
				cr = info
			if itemLength > 8:
				data.advance((itemLength - 8) * 4)
			x, y, width, height = struct.unpack("<ffff", info[4:20])
			if emptyAtlasPoint is not None:
				if width == 0 and height == 0:
					charid = int.from_bytes(info[:4], byteorder="little")
					print(f"Relocating 0x0 character U+{charid:x} to ({emptyAtlasPoint[0]}, {emptyAtlasPoint[1]})")
					info[4:12] = struct.pack("<ff", emptyAtlasPoint[0], emptyAtlasPoint[1])
			if x > atlasWidth:
				info[4:8] = self.AtlasWidth
			if y > atlasHeight:
				info[8:12] = self.AtlasHeight
			self.Array += info
		if not lf and cr is not None:
			print(f"No 0x0A LF character found, copying one from 0x0D CR")
			arrayLength = int.from_bytes(self.Array[0:4], byteorder="little")
			arrayLength += 1
			arrayLengthBytes = arrayLength.to_bytes(4, byteorder="little")
			cr[0:4] = (0x0A).to_bytes(4, byteorder="little")
			self.Array = arrayLengthBytes + cr + self.Array[4:]
			self.CharacterCount = arrayLengthBytes


	def _fromGame(self, data, filename, emptyAtlasPoint):
		data = DataScanner(data)
		self.Header = data.read(4 * 7)
		self.Filename = data.readString()
		if self.type == "Hima":
			self.BeforeFontName = data.read(4)
		else:
			self.BeforeFontName = bytes()
		self.FontName = data.readString()
		# Font face data
		self.PointSize = data.read(4)
		self.Padding = data.read(4)
		self.LineHeight = data.read(4)
		self.Baseline = data.read(4)
		self.Ascender = data.read(4)
		self.Descender = data.read(4)
		self.CenterLine = data.read(4)
		self.SuperscriptOffset = data.read(4)
		self.SubscriptOffest = data.read(4)
		self.SubSize = data.read(4)
		self.Underline = data.read(4)
		self.UnderlineThickness = data.read(4)
		self.TabWidth = data.read(4)
		self.CharacterCount = data.read(4)
		self.AtlasWidth = data.read(4)
		self.AtlasHeight = data.read(4)

		self.AfterFontFace = data.read(4 * 8)
		self._readArray(data, 8, emptyAtlasPoint)
		self.Footer = data.rest()

	def _fromAssetCreator(self, data, filename, emptyAtlasPoint):
		data = DataScanner(data)
		self.Header = data.read(4 * 15)
		self.Filename = data.readString()
		self.BeforeFontName = data.read(4 * 7)
		self.FontName = data.readString()
		# Font face data
		self.PointSize = data.read(4)
		self.Scale = data.read(4)
		self.CharacterCount = data.read(4)
		self.LineHeight = data.read(4)
		self.Baseline = data.read(4)
		self.Ascender = data.read(4)
		self.CapHeight = data.read(4)
		self.Descender = data.read(4)
		self.CenterLine = data.read(4)
		self.SuperscriptOffset = data.read(4)
		self.SubscriptOffest = data.read(4)
		self.SubSize = data.read(4)
		self.Underline = data.read(4)
		self.UnderlineThickness = data.read(4)
		self.strikethrough = data.read(4)
		self.strikethroughThickness = data.read(4)
		self.TabWidth = data.read(4)
		self.Padding = data.read(4)
		self.AtlasWidth = data.read(4)
		self.AtlasHeight = data.read(4)

		self.AfterFontFace = data.read(4 * 3)
		self._readArray(data, 9, emptyAtlasPoint)
		self.Footer = data.rest()

def combineFonts(original: FontFile, new: FontFile):
	out = bytes()
	out += original.Header
	out += original.Filename
	out += original.BeforeFontName
	out += new.FontName

	out += new.PointSize
	out += new.Padding
	out += new.LineHeight
	out += new.Baseline
	out += new.Ascender
	out += new.Descender
	out += new.CenterLine
	out += new.SuperscriptOffset
	out += new.SubscriptOffest
	out += new.SubSize
	out += new.Underline
	out += new.UnderlineThickness
	out += new.TabWidth
	out += new.CharacterCount
	out += new.AtlasWidth
	out += new.AtlasHeight

	out += original.AfterFontFace
	out += new.Array
	out += original.Footer

	return out

# Finds a size x size completely blank spot in the atlas
# Can be used for whitespace character relocation
def findEmptyAtlasPoint(atlas, size):
	atlasWidth = int.from_bytes(atlas[0:4], byteorder="little")
	atlasHeight = int.from_bytes(atlas[4:8], byteorder="little")
	atlasSize = int.from_bytes(atlas[56:60], byteorder="little")
	atlasData = atlas[60:]
	if atlasWidth * atlasHeight != atlasSize:
		print("Atlas doesn't match width and height!  This shouldn't happen")
		return None
	distance = size // 2
	stringToFind = b"\0" * size
	pos = 0
	try:
		while True:
			pos = atlasData.index(stringToFind, pos)
			offsets = []
			for i in range(-distance, distance+1):
				offset = ((i * atlasWidth) + pos) % atlasSize
				offsets.append(offset)
				if atlasData[offset:offset+size] != stringToFind:
					pos += 1
					break
			else:
				y = pos // atlasWidth
				y = atlasHeight - 1 - y # Texture2Ds are flipped
				x = pos % atlasWidth + distance
				return (x, y)
	except ValueError:
		return None


if len(sys.argv) > 4:
	atlasFN = sys.argv[1]
	behaviourFN = sys.argv[2]
	originalFN = sys.argv[3]
	outFN = sys.argv[4]
else:
	if len(sys.argv) < 4:
		print("Usage: " + sys.argv[0] + " [newAtlas.dat] newMonoBehaviour.dat originalMonoBehaviour.dat outputFolder")
		exit()

	behaviourFN = sys.argv[1]
	originalFN = sys.argv[2]
	outFN = sys.argv[3]

if not os.path.isdir(outFN):
	print("Output folder " + outFN + " must be a directory!")
	exit()

emptyAtlasPoint = None
if len(sys.argv) > 4:
	with open(atlasFN, "rb") as atlasFile:
		atlas = DataScanner(atlasFile.read())
	atlasOut = b""
	if int.from_bytes(atlas.peek(4), byteorder="little") not in range(8, 32):
		atlas.advance(4 * 7)
		atlasName = atlas.readString()
		atlas.advance(4 * 4)
	else:
		atlasName = atlas.readString()
	atlasOut += atlasName
	atlasRest = atlas.rest()
	emptyAtlasPoint = findEmptyAtlasPoint(atlasRest, 13)
	if len(sys.argv) > 5 and sys.argv[5] == "2017":
		atlasOut += atlasRest[:40]
		atlasOut += atlasRest[40:44] * 3 # Unity 2017 split m_wrap into U, V, and W
		atlasOut += atlasRest[44:]
	else:
		atlasOut += atlasRest

with open(originalFN, "rb") as originalFile:
	original = FontFile(originalFile.read(), originalFN)
with open(behaviourFN, "rb") as behaviourFile:
	behaviour = FontFile(behaviourFile.read(), behaviourFN, emptyAtlasPoint)

if len(sys.argv) > 4:
	atlasName = readString(atlasName)
	with open(outFN + "/" + original.filename + " Atlas_Texture2D.dat", "wb") as outFile:
		outFile.write(atlasOut)
with open(outFN + "/" + original.filename + "_TextMeshProFont.dat", "wb") as outFile:
	outFile.write(combineFonts(original=original, new=behaviour))

