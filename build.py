import re
import subprocess
import sys
import os
import pathlib
import shutil
import argparse
import json
from typing import List
from urllib.request import Request, urlopen
from warnings import catch_warnings

# Get the github ref
GIT_TAG = None
GIT_REF = os.environ.get("GITHUB_REF")  # Github Tag / Version info
if GIT_REF is not None:
    GIT_TAG = GIT_REF.split("/")[-1]
    print(f"--- Git Ref: {GIT_REF} Git Tag: {GIT_TAG} ---")

chapter_to_chapter_number = {
    "onikakushi": 1,
    "watanagashi": 2,
    "tatarigoroshi": 3,
    "himatsubushi": 4,
    "meakashi": 5,
    "tsumihoroboshi": 6,
    "minagoroshi": 7,
    "matsuribayashi": 8,
    "rei": 9,
}

class BuildVariant:
    def __init__(self, short_description, chapter, unity, system, target_crc32=None, translation_default=False):
        self.chapter = chapter
        self.unity = unity
        self.system = system
        self.target_crc32 = target_crc32
        self.chapter_number = chapter_to_chapter_number[chapter]
        self.data_dir = f"HigurashiEp{self.chapter_number:02}_Data"
        self.translation_default = translation_default
        self.short_description = short_description

    def get_build_command(self) -> str:
        args = [self.chapter, self.unity, self.system]

        if self.target_crc32 is not None:
            args.append(self.target_crc32)

        return " ".join(args)

    def get_translation_sharedassets_name(self) -> str:
        operatingSystem = None
        if self.system == "win":
            operatingSystem = "Windows"
        elif self.system == "unix":
            operatingSystem = "LinuxMac"
        elif self.system == "mac":
            operatingSystem = "Mac"
        else:
            raise Exception(f"Unknown system {self.system}")

        args = [operatingSystem, self.short_description, self.unity]

        if self.target_crc32 is not None:
            args.append(self.target_crc32)

        name_no_ext = "-".join(args)

        return f"{name_no_ext}.languagespecificassets"

# List of build variants for any given chapter
#
# There must be a corresponding vanilla sharedassets0.assets file located at:
# assets\vanilla\{CHAPTER_NAME}[-{CRC32}]\{OS}-{UNITY_VERSION}\sharedassets0.assets
# for each entry.
chapter_to_build_variants = {
    "onikakushi": [
        BuildVariant("GOG-MG-Steam",        "onikakushi", "5.2.2f1", "win", translation_default=True),
        BuildVariant("GOG-MG-Steam",        "onikakushi", "5.2.2f1", "unix"),
    ],
    "watanagashi": [
        BuildVariant("GOG-MG-Steam",        "watanagashi", "5.2.2f1", "win", translation_default=True),
        BuildVariant("GOG-MG-Steam",        "watanagashi", "5.2.2f1", "unix"),
    ],
    "tatarigoroshi": [
        BuildVariant("GOG-Steam",           "tatarigoroshi", "5.4.0f1", "win", translation_default=True),
        BuildVariant("GOG-Steam",           "tatarigoroshi", "5.4.0f1", "unix"),
        BuildVariant("MG",                  "tatarigoroshi", "5.3.5f1", "win"),
        BuildVariant("Legacy",              "tatarigoroshi", "5.3.4p1", "win"),
        BuildVariant("MG",                  "tatarigoroshi", "5.3.4p1", "unix"),
    ],
    "himatsubushi": [
        BuildVariant("GOG-MG-Steam",        "himatsubushi", "5.4.1f1", "win", translation_default=True),
        BuildVariant("GOG-MG-Steam",        "himatsubushi", "5.4.1f1", "unix"),
    ],
    "meakashi": [
        BuildVariant("MG-Steam-GOG_old",    "meakashi", "5.5.3p3", "win", translation_default=True), #also used by GOG old?
        BuildVariant("MG-Steam-GOG_old",    "meakashi", "5.5.3p3", "unix"), #also used by GOG old?
        BuildVariant("GOG",                 "meakashi", "5.5.3p1", "win"),
        BuildVariant("GOG",                 "meakashi", "5.5.3p1", "unix"),
    ],
    "tsumihoroboshi": [
        BuildVariant("GOG-MG-Steam",        "tsumihoroboshi", "5.5.3p3", "win", translation_default=True),
        BuildVariant("GOG-MG-Steam",        "tsumihoroboshi", "5.5.3p3", "unix"),
        # While GOG Windows is ver 5.6.7f1, we actually downgrade back to 5.5.3p3 in the installer, so we don't need this version.
        #'tsumihoroboshi 5.6.7f1 win'
    ],
    "minagoroshi": [
        BuildVariant("GOG-MG-Steam",        "minagoroshi", "5.6.7f1", "win", translation_default=True),
        BuildVariant("GOG-MG-Steam",        "minagoroshi", "5.6.7f1", "unix"),
        # While GOG Windows is ver 5.6.7f1, we actually downgrade back to 5.5.3p3 in the installer, so we don't need this version.
        # 'matsuribayashi 5.6.7f1 win'
        # 'matsuribayashi 5.6.7f1 unix'
    ],
    "matsuribayashi": [
        # Based on the GOG MacOS sharedassets, but works on Linux too.
        # Working on:
        # - Linux Steam (2023-07-09)
        # - Linux GOG (2023-07-09)
        # - MacOS GOG  (2023-07-09)
        BuildVariant("GOG-MG-Steam",    "matsuribayashi", "2017.2.5", "unix"),

        # NOTE: I'm 99% certain this file is no longer used, as we just upgrade the entire GOG/Mangagamer game
        # Special version for GOG/Mangagamer Linux with SHA256:
        # A200EC2A85349BC03B59C8E2F106B99ED0CBAAA25FC50928BB8BA2E2AA90FCE9
        # CRC32L 51100D6D
        # BuildVariant("GOG-MG",              "matsuribayashi", "2017.2.5", "unix", "51100D6D"), # TO BE REMOVED

        BuildVariant("GOG-MG-Steam",        "matsuribayashi", "2017.2.5", "win", translation_default=True),
    ],
    'rei': [
       BuildVariant("GOG-Steam-MG_old",     "rei", "2019.4.3", "win", translation_default=True),
       BuildVariant("MG",                   "rei", "2019.4.4", "win"),
       BuildVariant("GOG-Steam-MG_old",     "rei", "2019.4.3", "unix"),
       BuildVariant("MG",                   "rei", "2019.4.4", "unix"),
    ],
}

def is_windows():
    return sys.platform == "win32"


def call(args, **kwargs):
    print("running: {}".format(args))
    retcode = subprocess.call(
        args, shell=is_windows(), **kwargs
    )  # use shell on windows
    if retcode != 0:
        raise Exception(f"ERROR: {args} exited with retcode: {retcode}")


def download(url):
    print(f"Starting download of URL: {url}")
    call(["curl", "-OJLf", url])


def seven_zip_extract(input_path, outputDir=None):
    args = ["7z", "x", input_path, "-y"]
    if outputDir:
        args.append("-o" + outputDir)

    call(args)

def seven_zip_compress(input_path, output_path):
    args = ["7z", "a", "-md=512m", output_path, input_path, "-y"]

    call(args)


def get_chapter_name_and_translation_from_git_tag():
    returned_chapter_name = None
    translation = False

    if GIT_TAG is None:
        raise Exception(
            "'github_actions' was selected, but environment variable GITHUB_REF was not set - are you sure you're running this script from Github Actions?"
        )
    else:
        # Look for the chapter name to build in the git tag
        tag_fragments = [x.lower() for x in re.split("[\W_]", GIT_REF)]

        if "all" in tag_fragments:
            returned_chapter_name = "all"
        else:
            for chapter_name in chapter_to_build_variants.keys():
                if chapter_name.lower() in tag_fragments:
                    returned_chapter_name = chapter_name
                    break

        if "translation" in tag_fragments:
            translation = True

    return returned_chapter_name, translation


def get_build_variants(selected_chapter: str) -> List[BuildVariant]:
    if selected_chapter == "all":
        commands = []
        for command in chapter_to_build_variants.values():
            commands.extend(command)
        return commands
    elif selected_chapter in chapter_to_build_variants:
        return chapter_to_build_variants[selected_chapter]
    else:
        raise Exception(
            f"Unknown Chapter {selected_chapter} - please update the build.py script"
        )


class LastModifiedManager:
    savePath = 'lastModified.json'

    def __init__(self) -> None:
        self.lastModifiedDict = {}

        if os.path.exists(LastModifiedManager.savePath):
            with open(LastModifiedManager.savePath, 'r') as handle:
                self.lastModifiedDict = json.load(handle)

    def getRemoteLastModified(url: str):
        httpResponse = urlopen(Request(url, headers={"User-Agent": ""}))
        return httpResponse.getheader("Last-Modified").strip()

    def isRemoteModifiedAndUpdateMemory(self, url: str):
        """
        Checks whether a URL has been modified compared to the in-memory database,
        and updates the in-memory database with the new date modified time.

        NOTE: calling this function twice will return true the first time, then false
        the second time (assuming remote has not been updated), as the first call
        updates the in-memory database
        """
        remoteLastModified = LastModifiedManager.getRemoteLastModified(url)
        localLastModified = self.lastModifiedDict.get(url)

        if localLastModified is not None and localLastModified == remoteLastModified:
            print(f"LastModifiedManager [{url}]: local and remote dates the same {localLastModified}")
            return False

        print(f"LastModifiedManager [{url}]: local {localLastModified} and remote {remoteLastModified} are different")
        self.lastModifiedDict[url] = remoteLastModified
        return True

    def save(self):
        """
        Save the in-memory database to file, so it persists even when the program is closed.
        """
        with open(LastModifiedManager.savePath, 'w') as handle:
            json.dump(self.lastModifiedDict, handle)

if sys.version_info < (2, 7):
    print(">>>> ERROR: This script does not work on Python 2.7")
    exit(-1)

if sys.version_info > (3, 10):
    print(">>>> WARNING: This script probably does not work on Python 3.11 because unitypack uses old version of decrunch which does not build. Use Python 3.10 or below if you have this error.")

lastModifiedManager = LastModifiedManager()

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Download and Install dependencies for ui editing scripts, then run build"
)
parser.add_argument(
    "chapter",
    help='The chapter to build, or "all" for all chapters',
    choices=["all", "github_actions"] + list(chapter_to_build_variants.keys()),
)
parser.add_argument("--force-download", default=False, action='store_true')
parser.add_argument("--disable-translation", default=False, action='store_true')
args = parser.parse_args()

force_download = args.force_download

# Get chapter name from git tag if "github_actions" specified as the chapter
chapter_name = args.chapter
if chapter_name == "github_actions":
    chapter_name, translation = get_chapter_name_and_translation_from_git_tag()
    if chapter_name is None:
        print(
            f">>>> WARNING: No chapter name (or 'all') was found in git tag {GIT_TAG} - skipping building .assets"
        )
        exit(0)

# NOTE: For now, translation archive output is enabled by default, as most of the time this script will be used for translators
translation = True

if args.disable_translation:
    translation = False

# Get a list of build variants (like 'onikakushi 5.2.2f1 win') depending on commmand line arguments
build_variants = get_build_variants(chapter_name)
build_variants_list = "\n - ".join([b.get_build_command() for b in build_variants])
print(f"-------- Build Started --------")
print(f"Chapter: [{chapter_name}] | Translation Archive Output: [{('Enabled' if translation else 'Disabled')}]")
print(f"Variants:")
print(f" - {build_variants_list}")
print(f"-------------------------------")
print()

# Install python dependencies
print("Installing python dependencies")
call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Download and extract the vanilla assets
assets_path = "assets"
vanilla_archive = "vanilla.7z"
assets_url = "http://07th-mod.com/archive/vanilla.7z"
vanilla_folder_path = os.path.join(assets_path, "vanilla")
vanilla_fully_extracted = os.path.exists(vanilla_folder_path) and not os.path.exists(vanilla_archive)
if lastModifiedManager.isRemoteModifiedAndUpdateMemory(assets_url) or force_download or not vanilla_fully_extracted:
    print("Downloading and Extracting Vanilla assets")
    pathlib.Path(vanilla_archive).unlink(missing_ok=True)
    if os.path.exists(vanilla_folder_path):
        shutil.rmtree(vanilla_folder_path)

    download(assets_url)
    seven_zip_extract(vanilla_archive)

    # Remove the archive to indicate extraction was successful
    pathlib.Path(vanilla_archive).unlink(missing_ok=True)
    lastModifiedManager.save()
else:
    print("Vanilla archive already extracted - skipping")

# Download and extract UABE
uabe_folder = "64bit"
uabe_archive = "AssetsBundleExtractor_2.2stabled_64bit_with_VC2010.zip"
uabe_url = f"http://07th-mod.com/archive/{uabe_archive}"
uabe_fully_extracted = os.path.exists(uabe_folder) and not os.path.exists(uabe_archive)
if lastModifiedManager.isRemoteModifiedAndUpdateMemory(uabe_url) or force_download or not uabe_fully_extracted:
    print("Downloading and Extracting UABE")
    pathlib.Path(uabe_archive).unlink(missing_ok=True)
    if os.path.exists(uabe_folder):
        shutil.rmtree(uabe_folder)

    # The default Windows github runner doesn't have the 2010 VC++ redistributable preventing UABE from running
    # This zip file bundles the required DLLs (msvcr100.dll & msvcp100.dll) so it's not required
    download(uabe_url)
    seven_zip_extract(uabe_archive)

    # Remove the archive to indicate extraction was successful
    pathlib.Path(uabe_archive).unlink(missing_ok=True)
    lastModifiedManager.save()
else:
    print("UABE already extracted - skipping")


# Add UABE to PATH
uabe_folder = os.path.abspath(uabe_folder)
os.environ["PATH"] += os.pathsep + os.pathsep.join([uabe_folder])

# If rust is not installed, download binary release of ui comopiler
# This is mainly for users running this script on their own computer
working_cargo = False
try:
    subprocess.check_output("cargo -v")
    print(
        "Found working Rust/cargo - will compile ui-compiler.exe using repository sources"
    )
    working_cargo = True
except:
    print("No working Rust/cargo found - download binary release of UI compiler...")
    download(
        "https://github.com/07th-mod/ui-editing-scripts/releases/latest/download/ui-compiler.exe"
    )

# Build all the requested variants
for build_variant in build_variants:
    print(f"Building .assets for {build_variant.get_build_command()}...")
    if working_cargo:
        call(f"cargo run {build_variant.get_build_command()}")
    else:
        call(f"ui-compiler.exe {build_variant.get_build_command()}")

    if translation:
        source_sharedassets = os.path.join("output", build_variant.data_dir, "sharedassets0.assets")
        translation_data_dir = os.path.join("output/translation", build_variant.data_dir)
        destination_sharedassets = os.path.join(translation_data_dir, build_variant.get_translation_sharedassets_name())

        os.makedirs(translation_data_dir, exist_ok=True)
        shutil.copyfile(source_sharedassets, destination_sharedassets)

        if build_variant.translation_default:
            destination_default_sharedassets = os.path.join(translation_data_dir, "sharedassets0.assets")
            shutil.copyfile(source_sharedassets, destination_default_sharedassets)

if translation:
    containing_folder = "output"
    output_path = "output/translation.7z"
    if os.path.exists(output_path):
        os.remove(output_path)

    seven_zip_compress('output/translation', output_path)