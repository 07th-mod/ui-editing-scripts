import sys
import os
from unitypack.asset import Asset


if len(sys.argv) < 3:
	print("This tool dumps assets from asset files for use in diffing\nUsage: " + sys.argv[0] + " assetfile.assets outputFolder\nWill extract all assets from the input file and write them to outputFolder/####.dat")
	exit()

with open(sys.argv[1], "rb") as assetsFile:
	asset = Asset.from_file(assetsFile)
	for id, obj in asset.objects.items():
		assetsFile.seek(obj.data_offset)
		data = assetsFile.read(obj.size)
		with open(os.path.join(sys.argv[2], str(id) + ".dat"), "wb") as outfile:
			outfile.write(data)