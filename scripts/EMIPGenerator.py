import sys
import os
import re
from PIL import Image
from PIL import ImageOps
from unitypack.asset import Asset

if len(sys.argv) < 4:
	print("Usage: " + sys.argv[0] + " assetfile.assets inputFolder outputFile.emip\nInput folder should contain files whose names start with the object ID they want to replace.")
	exit()

if not os.path.isdir(sys.argv[2]):
	print("Input folder " + sys.argv[2] + " must be a directory!")
	exit()

class AssetEdit:
	def __init__(self, file, id, name, type):
		self.file = file
		self.id = id
		self.name = name
		self.type = type
		self.shouldDecode = False

	@property
	def filePath(self):
		return sys.argv[2] + "/" + self.file

	def pngToTexture2D(self, pngData, unityVersion):
		image = Image.open(self.filePath)
		image = ImageOps.flip(image)
		imageData = image.convert("RGBA").tobytes()
		output = len(self.name).to_bytes(4, byteorder="little")
		output += self.name.encode("utf-8")
		output += b"\0" * ((4 - len(self.name)) % 4)
		output += image.width.to_bytes(4, byteorder="little")
		output += image.height.to_bytes(4, byteorder="little")
		output += len(imageData).to_bytes(4, byteorder="little")
		output += (4).to_bytes(4, byteorder="little") # m_TextureFormat
		output += (1).to_bytes(4, byteorder="little") # m_MipCount
		output += b"\0\x01\0\0" # Flags
		output += (1).to_bytes(4, byteorder="little") # m_ImageCount
		output += (2).to_bytes(4, byteorder="little") # m_TextureDimension
		output += (2).to_bytes(4, byteorder="little") # m_FilterMode
		output += (2).to_bytes(4, byteorder="little") # m_Aniso
		output += (0).to_bytes(4, byteorder="little") # m_MipBias
		if unityVersion[0] == 5:
			output += (1).to_bytes(4, byteorder="little") # m_WrapMode
		elif unityVersion[0] == 2017:
			output += (1).to_bytes(4, byteorder="little") * 3 # m_wrap{U,V,W}
		else:
			sys.stderr.write("Warning: Unrecognized Unity version: " + str(unityVersion[0]))
		output += (0).to_bytes(4, byteorder="little") # m_LightmapFormat
		output += (1).to_bytes(4, byteorder="little") # m_ColorSpace
		output += len(imageData).to_bytes(4, byteorder="little")
		output += imageData
		if self.hasStream:
			output += b"\0" * 12 # Empty Streaming Data
		return output

	def loadTexture2DInfo(self, assets, bundle):
		self.shouldDecode = True
		obj = assets.objects[self.id]
		data = bundle[obj.data_offset:(obj.data_offset + obj.size)]
		length = int.from_bytes(data[0:4], byteorder='little')
		paddedLength = length + (4 - length) % 4
		self.name = data[4:4+length].decode('utf-8')
		arrayPos = paddedLength + 4 * 15
		arrayLength = int.from_bytes(data[arrayPos:arrayPos+4], byteorder="little")
		paddedArrayLength = arrayLength + (4 - arrayLength) % 4
		if arrayPos + 4 + paddedArrayLength == len(data):
			self.hasStream = False
		elif arrayPos + 4 + paddedArrayLength <= len(data) - 12:
			self.hasStream = True
		else:
			print(f"Couldn't figure out if {self.name} has a stream or not.  Comparing {arrayPos + 4 + paddedArrayLength} to {len(data)}")
			self.hasStream = True

	def getAssetInfo(self, assets, bundle):
		if self.id is None:
			for id, obj in assets.objects.items():
				try:
					objType = obj.type
					if objType != self.type: continue
				except:
					# Special case handling for newer files that fail to read type id
					if self.type == "TextMeshProFont" and obj.type_id < 0:
						objType = self.type
						pass
					else:
						continue
				
				# UnityPack is broken and overreads its buffer if we try to use it to automatically decode things, so instead we use this sometimes-working thing to decode the name
				data = bundle[obj.data_offset:(obj.data_offset + obj.size)]
				
				name = None
				try:
					name = obj.read()["m_Name"]
				except:
					length = int.from_bytes(data[0:4], byteorder='little')
					# Things often store their length in the beginning of the file
					# Note: the `len(self.name) * 4` is the maximum length the string `self.name` could be if it used high unicode characters
					if length >= len(self.name) and length + 4 <= len(data) and length < len(self.name) * 4:
						name = data[4:4+length].decode('utf-8')
					# TextMeshPro assets store their name here
					elif len(data) > 32:
						length = int.from_bytes(data[28:32], byteorder='little')
						if length + 4 <= len(data) and length < 40:
							name = data[32:32+length].decode('utf-8')
				if name is not None:
					if self.name == name:
						self.id = id
						if objType == "Texture2D" and self.file[-4:] == ".png":
							print(f"Will replace object #{id} with contents of {self.file} converted to a Texture2D")
							self.loadTexture2DInfo(assets, bundle)
						else:
							print(f"Will replace object #{id} with contents of {self.file}")
						break
		else:
			if self.file[-4:] == ".png":
				self.loadTexture2DInfo(assets, bundle)
				print(f"Will replace object #{self.id} with contents of {self.file} converted to a Texture2D")
			else:
				print(f"Will replace object #{self.id} with contents of {self.file}")

		if self.id == None:
			print(f"Couldn't find object named {self.name} for {self.file}, skipping")
			return
		obj = assets.objects[self.id]
		self.type = obj.type_id

	def bytes(self, unityVersion):
		out = (2).to_bytes(4, byteorder='little') # Unknown
		out += b"\0" * 3 # Unknown
		out += self.id.to_bytes(4, byteorder='little') # Unknown
		out += b"\0" * 4 # Unknown
		out += self.type.to_bytes(4, byteorder='little', signed=True) # Type
		out += b"\xff" * 2 # Unknown
		with open(self.filePath, "rb") as file:
			fileBytes = file.read()
			if self.shouldDecode:
				fileBytes = self.pngToTexture2D(fileBytes, unityVersion)
			out += len(fileBytes).to_bytes(4, byteorder='little') # Payload Size
			out += b"\0" * 4 # Unknown
			out += fileBytes # Payload
		return out

def generateHeader(numEdits):
	header = b"EMIP" # Magic
	header += b"\0" * 4 # Unknown
	header += (1).to_bytes(4, byteorder='big') # Number of files
	header += b"\0" * 4 # Unknown
	if os.path.abspath(sys.argv[1])[1] == ":": # Windows paths will be read properly, UNIX paths won't since UABE will be run with wine, so use a relative path
		path = os.path.abspath(sys.argv[1]).encode('utf-8')
	else:
		path = sys.argv[1].encode('utf-8')
	header += len(path).to_bytes(2, byteorder='little') # Path length
	header += path # File path
	header += numEdits.to_bytes(4, byteorder='little') # Number of file changes
	return header

edits = []

for file in os.listdir(sys.argv[2]):
	if file[0] == ".": continue
	matches = re.match(r"^(\d+).*", file)
	if matches:
		edits.append(AssetEdit(file, int(matches.group(1)), None, None))
	else:
		name = os.path.splitext(file)[0]
		parts = name.split("_")
		if len(parts) < 2: continue
		edits.append(AssetEdit(file, None, "_".join(parts[:-1]), parts[-1]))

with open(sys.argv[1], "rb") as assetsFile:
	bundle = assetsFile.read()
	unityVersion = [int(x) for x in bundle[20:28].decode("utf-8").rstrip("\0").split(".")[:2]]
	assetsFile.seek(0)
	assets = Asset.from_file(assetsFile)
	for edit in edits:
		edit.getAssetInfo(assets, bundle)
	edits = [x for x in edits if x.id != None]

edits = sorted(edits, key=lambda x: x.id)

with open(sys.argv[3], "wb") as outputFile:
	outputFile.write(generateHeader(len(edits)))
	for edit in edits:
		outputFile.write(edit.bytes(unityVersion))

