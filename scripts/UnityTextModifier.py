import sys
import os
import json
import unitypack
from unitypack.asset import Asset

if len(sys.argv) < 4:
	print("Usage: " + sys.argv[0] + " assetfile.assets edits.json outputfolder\nEdits.json should be an array of objects with the fields 'CurrentEnglish', 'CurrentJapanese', 'NewEnglish', and 'NewJapanese'.  An optional 'Discriminator' field can be added if multiple texts have the same English and Japanese values.");
	exit()

if not os.path.isdir(sys.argv[3]):
	print("Output folder " + sys.argv[3] + " must be a directory!")
	exit()

class ScriptEdit:
	@staticmethod
	def truncateString(string):
		trimmed = False
		if len(string) > 60:
			trimmed = True
			string = string[:60]
		if "\n" in string:
			trimmed = True
			string = string.partition("\n")[0].rstrip()
		if trimmed:
			string += "..."
		return string

	def __init__(self, currentEnglish, currentJapanese, newEnglish, newJapanese, discriminator=None):
		self.currentEnglish = currentEnglish
		self.currentJapanese = currentJapanese
		self.newEnglish = newEnglish
		self.newJapanese = newJapanese
		self.discriminator = discriminator
		if (newJapanese is None) != (currentJapanese is None):
			raise ValueError("Include either both NewJapanese and CurrentJapanese or neither, but not just one!")
		self.shortString = ScriptEdit.truncateString(self.currentEnglish) if newJapanese is None else ScriptEdit.truncateString(self.currentEnglish) + " / " + ScriptEdit.truncateString(self.currentJapanese)


	@staticmethod
	def fromJSON(json):
		return ScriptEdit(json["CurrentEnglish"], json.get("CurrentJapanese"), json["NewEnglish"], json.get("NewJapanese"), json.get("Discriminator"))

	@staticmethod
	def bytesFromString(string):
		strBytes = string.encode('utf-8')
		out = len(strBytes).to_bytes(4, byteorder='little')
		out += strBytes
		out += b"\0" * ((4 - len(strBytes)) % 4)
		return out

	@property
	def expectedBytes(self):
		if self.currentJapanese is not None:
			return self.bytesFromString(self.currentEnglish) + self.bytesFromString(self.currentJapanese)
		return self.bytesFromString(self.currentEnglish)

	@property
	def newBytes(self):
		if self.currentJapanese is not None:
			return self.bytesFromString(self.newEnglish) + self.bytesFromString(self.newJapanese)
		return self.bytesFromString(self.newEnglish)

	def findInAssetBundle(self, bundle):
		search = self.expectedBytes
		offsets = []
		start = 0
		while True:
			offset = bundle.find(search, start)
			if offset == -1:
				break
			offsets.append(offset)
			start = offset + 1
		if len(offsets) == 0:
			raise IndexError(f"WARNING: No asset found for {self.shortString}")
		if self.discriminator == None:
			if len(offsets) > 1:
				raise IndexError(f"WARNING: Multiple assets found for {self.shortString}, candidates are " + ", ".join(f"{index}: 0x{offset:x}" for index, offset in enumerate(offsets)) + ". Please add a field like 'Discriminator: 0' to indicate which block should apply to which asset (do NOT use quotes around the number, do not use the raw address). For an example, see https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts#unitytextmodifier")
			self.offset = offsets[0]
		else:
			if len(offsets) <= self.discriminator:
				raise IndexError(f"WARNING: Not enough offsets found for {self.shortString} to meet request for #{self.discriminator}, there were only {len(offsets)}")
			self.offset = offsets[self.discriminator]

	def checkObject(self, id, object, bundle):
		if obj.data_offset <= self.offset and obj.data_offset + obj.size >= self.offset:
			self.id = id
			self.currentData = bundle[obj.data_offset:(obj.data_offset + obj.size)]
			expectedBytes = self.expectedBytes
			smallOffset = self.currentData.find(expectedBytes)
			self.newData = self.currentData[:smallOffset] + self.newBytes + self.currentData[(smallOffset + len(expectedBytes)):]
			print(f"Found {self.shortString} in object #{id}")

	def write(self, folder):
		try:
			self.newData
		except:
			print(f"Failed to find object id for {self.shortString}!")
			return
		filename = folder + "/" + str(self.id) + ".dat"
		with open(filename, "wb") as outputFile:
			outputFile.write(self.newData)

	def __repr__(self):
		string = f"ScriptEdit(currentEnglish: {self.currentEnglish}, currentJapanese: {self.currentJapanese}, newEnglish: {self.newEnglish}, newJapanese: {self.newJapanese}"
		if self.discriminator != None:
			string += f", discriminator: {self.discriminator}"
		try: string += f", offset: 0x{self.offset:x}"
		except: pass
		return string + ")"

	def __str__(self):
		try: return f"<ScriptEdit for position 0x{self.offset:x}>"
		except: return "<ScriptEdit for unknown position>"

warning_count = 0

with open(sys.argv[2], encoding="utf-8") as jsonFile:
	edits = [ScriptEdit.fromJSON(x) for x in json.load(jsonFile)]

with open(sys.argv[1], "rb") as assetsFile:
	bundle = assetsFile.read()
	newEdits = []
	for edit in edits:
		try:
			edit.findInAssetBundle(bundle)
			newEdits.append(edit)
			print(f"Found {edit.shortString} at offset 0x{edit.offset:x}")
		except IndexError as e:
			print(e)
			warning_count =+ 1

	edits = newEdits

	assetsFile.seek(0)
	assets = Asset.from_file(assetsFile, legacy_mode=True)
	for id, obj in assets.objects.items():
		for edit in edits:
			edit.checkObject(id, obj, bundle)
	for edit in edits:
		edit.write(sys.argv[3])

if warning_count > 0:
	print(">>>>>>>> ONE OR MORE WARNINGS OCCURRED, please check logs! <<<<<<<<<")
