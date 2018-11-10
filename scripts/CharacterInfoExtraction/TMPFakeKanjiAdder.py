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
		for _ in range(length):
			info = bytearray(data.read(4 * 8))
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

	def toBytes(self):
		out = bytes()
		out += self.Header
		out += self.Filename
		out += self.BeforeFontName
		out += self.FontName

		out += self.PointSize
		out += self.Padding
		out += self.LineHeight
		out += self.Baseline
		out += self.Ascender
		out += self.Descender
		out += self.CenterLine
		out += self.SuperscriptOffset
		out += self.SubscriptOffest
		out += self.SubSize
		out += self.Underline
		out += self.UnderlineThickness
		out += self.TabWidth
		out += self.CharacterCount
		out += self.AtlasWidth
		out += self.AtlasHeight

		out += self.AfterFontFace
		out += self.Array
		out += self.Footer

		return out

	def fakeChars(self, charlist):
		zeroSizeCharInfo = None
		oldSize = int.from_bytes(self.Array[0:4], byteorder="little")
		existingChars = set()
		for i in range(oldSize):
			index = 4 + (i * 4 * 8)
			unicodescalar = int.from_bytes(self.Array[index:index+4], byteorder="little")
			existingChars.add(unicodescalar)
			if unicodescalar == 0x3000:
				zeroSizeCharInfo = bytearray(self.Array[index:index+32])
		if zeroSizeCharInfo is None:
			print("Starting character set should contain a U+3000 ideographic space to base fake kanji info off of.")
			return;
		newSize = oldSize
		newArray = bytearray(self.Array)
		for char in charlist:
			if char in existingChars:
				continue
			zeroSizeCharInfo[0:4] = char.to_bytes(4, byteorder="little")
			newArray.extend(zeroSizeCharInfo)
			existingChars.add(char)
			newSize += 1
		finalSizeInfo = newSize.to_bytes(4, byteorder="little")
		newArray[0:4] = finalSizeInfo
		self.CharacterCount = finalSizeInfo
		self.Array = bytes(newArray)

if len(sys.argv) <= 3:
	print("Usage: " + sys.argv[0] + " monobehaviour.dat charset.txt outputMonoBehaviour.dat")
	exit(0)

with open(sys.argv[1], "rb") as tmp:
	tmpAsset = FontFile(tmp.read(), sys.argv[1])

with open(sys.argv[2], "r", encoding="utf-8") as charsetFile:
	charsetText = charsetFile.read()
	chars = [ord(x) for x in charsetText]
tmpAsset.fakeChars(chars)
with open(sys.argv[3], "wb") as output:
	output.write(tmpAsset.toBytes())