import os
from sys import argv

path = argv[1]

assetsbundlePath = os.path.join(path, "sharedassets0.assets")
if os.path.exists(assetsbundlePath):
    with open(assetsbundlePath, "rb") as assetsBundle:
        unityVersion = assetsBundle.read(28)[20:].decode("utf-8").rstrip("\0")
    print(unityVersion)
else:
    print("Nothing found")
