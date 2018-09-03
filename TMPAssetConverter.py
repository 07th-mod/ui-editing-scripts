import sys
import os

if len(sys.argv) < 5:
	print("Usage: " + sys.argv[0] + " newAtlas.dat newMonoBehaviour.dat originalMonoBehaviour.dat outputFolder")
	exit()

if not os.path.isdir(sys.argv[4]):
	print("Output folder " + sys.argv[4] + " must be a directory!")
	exit()

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
		length = int.from_bytes(self.peek(4), byteorder='little')
		length += (4 - length) % 4
		return self.read(length + 4)

	def rest(self):
		return self.data[self.offset:]

with open(sys.argv[1], "rb") as atlasFile:
	atlas = DataScanner(atlasFile.read())
with open(sys.argv[2], "rb") as behaviourFile:
	behaviour = DataScanner(behaviourFile.read())

# Atlas Editing
atlasOut = b""
atlas.advance(4 * 7)
name = atlas.readString()
atlasOut += name
name = name[4:].decode('utf-8')
atlas.advance(4 * 4)
atlasOut += atlas.rest()
with open(sys.argv[4] + "/" + name + "_Texture2D.dat", "wb") as outFile:
	outFile.write(atlasOut)

# MonoBehaviour editing
behaviourOut = b""
with open(sys.argv[3], "rb") as originalFile:
	original = DataScanner(originalFile.read())
behaviourOut += original.read(4 * 7) # Unknown
behaviour.advance(4 * 15) # Unneeded stuff
originalName = original.readString()
newName = behaviour.readString()
if originalName != newName: # If these names don't match then the atlas's won't either, and we didn't ask for the original atlas file
	print("Asset names " + originalName[4:].decode("utf-8") + " and " + newName[4:].decode("utf-8") + " don't match, aborting!")
	exit()
behaviourOut += newName
behaviour.advance(4 * 6) # Unneeded stuff
original.advance(4) # Will be read from behaviour
behaviourOut += behaviour.read(4)
original.readString() # Font name, will be gotten from behaviour
behaviourOut += behaviour.readString() # Font name
original.advance(4 * 16) # Font face data, will be read and converted from behaviour
# Read font face data, is in a completely different order from the target
PointSize = behaviour.read(4)
Scale = behaviour.read(4)
CharacterCount = behaviour.read(4)
LineHeight = behaviour.read(4)
Baseline = behaviour.read(4)
Ascender = behaviour.read(4)
CapHeight = behaviour.read(4)
Descender = behaviour.read(4)
CenterLine = behaviour.read(4)
SuperscriptOffset = behaviour.read(4)
SubscriptOffest = behaviour.read(4)
SubSize = behaviour.read(4)
Underline = behaviour.read(4)
UnderlineThickness = behaviour.read(4)
strikethrough = behaviour.read(4)
strikethroughThickness = behaviour.read(4)
TabWidth = behaviour.read(4)
Padding = behaviour.read(4)
AtlasWidth = behaviour.read(4)
AtlasHeight = behaviour.read(4)
# Write font face data
behaviourOut += PointSize
behaviourOut += Padding
behaviourOut += LineHeight
behaviourOut += Baseline
behaviourOut += Ascender
behaviourOut += Descender
behaviourOut += CenterLine
behaviourOut += SuperscriptOffset
behaviourOut += SubscriptOffest
behaviourOut += SubSize
behaviourOut += Underline
behaviourOut += UnderlineThickness
behaviourOut += TabWidth
behaviourOut += CharacterCount
behaviourOut += AtlasWidth
behaviourOut += AtlasHeight
behaviour.advance(4 * 3) # Will read this from original
behaviourOut += original.read(4 * 8) # Other data
behaviourOut += behaviour.peek(4) # Char info array length
originalArrayLength = int.from_bytes(original.read(4), byteorder='little')
newArrayLength = int.from_bytes(behaviour.read(4), byteorder='little')
original.advance(originalArrayLength * 4 * 8) # We don't need this data
for i in range(newArrayLength):
	behaviourOut += behaviour.read(4 * 8)
	behaviour.advance(4) # One field is only in the new data so we need to remove it
behaviourOut += original.rest() # Rest of file can be copied from the original
with open(sys.argv[4] + "/" + os.path.basename(sys.argv[3]), "wb") as outFile:
	outFile.write(behaviourOut)
	
