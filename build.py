import re
import subprocess
import sys
import os
import pathlib
import shutil
import argparse
from typing import List

# Get the github ref
GIT_TAG = None
GIT_REF = os.environ.get("GITHUB_REF")  # Github Tag / Version info
if GIT_REF is not None:
    GIT_TAG = GIT_REF.split("/")[-1]
    print(f"--- Git Ref: {GIT_REF} Git Tag: {GIT_TAG} ---")

# List of build variants for any given chapter
#
# There must be a corresponding vanilla sharedassets0.assets file located at:
# assets\vanilla\{CHAPTER_NAME}[-{CRC32}]\{OS}-{UNITY_VERSION}\sharedassets0.assets
# for each entry.
chapter_to_build_variants = {
    "onikakushi": [
        "onikakushi 5.2.2f1 win",
        "onikakushi 5.2.2f1 unix",
    ],
    "watanagashi": [
        "watanagashi 5.2.2f1 win",
        "watanagashi 5.2.2f1 unix"
    ],
    "tatarigoroshi": [
        "tatarigoroshi 5.4.0f1 win",
        "tatarigoroshi 5.4.0f1 unix",
        "tatarigoroshi 5.3.5f1 win",
        "tatarigoroshi 5.3.4p1 win",
        "tatarigoroshi 5.3.4p1 unix",
    ],
    "himatsubushi": [
        "himatsubushi 5.4.1f1 win",
        "himatsubushi 5.4.1f1 unix"
    ],
    "meakashi": [
        "meakashi 5.5.3p3 win",
        "meakashi 5.5.3p3 unix",
        "meakashi 5.5.3p1 win",
        "meakashi 5.5.3p1 unix",
    ],
    "tsumihoroboshi": [
        "tsumihoroboshi 5.5.3p3 win",
        "tsumihoroboshi 5.5.3p3 unix"
        # While GOG Windows is ver 5.6.7f1, we actually downgrade back to 5.5.3p3 in the installer, so we don't need this version.
        #'tsumihoroboshi 5.6.7f1 win'
    ],
    "minagoroshi": [
        "minagoroshi 5.6.7f1 win",
        "minagoroshi 5.6.7f1 unix"
        # While GOG Windows is ver 5.6.7f1, we actually downgrade back to 5.5.3p3 in the installer, so we don't need this version.
        # 'matsuribayashi 5.6.7f1 win'
        # 'matsuribayashi 5.6.7f1 unix'
    ],
    "matsuribayashi": [
        "matsuribayashi 2017.2.5 unix",
        # Special version for GOG/Mangagamer Linux with SHA256:
        # A200EC2A85349BC03B59C8E2F106B99ED0CBAAA25FC50928BB8BA2E2AA90FCE9
        # CRC32L 51100D6D
        "matsuribayashi 2017.2.5 unix 51100D6D",
        "matsuribayashi 2017.2.5 win",
    ],
    'rei': [
        'rei 2019.4.3 win',
        'rei 2019.4.3 unix',
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


def get_chapter_name_from_git_tag():
    if GIT_TAG is None:
        raise Exception(
            "'github_actions' was selected, but environment variable GIT_REF was not set - are you sure you're running this script from Github Actions?"
        )
    else:
        # Look for the chapter name to build in the git tag
        tag_fragments = [x.lower() for x in re.split("[\W_]", GIT_REF)]

        if "all" in tag_fragments:
            return "all"
        else:
            for chapter_name in chapter_to_build_variants.keys():
                if chapter_name.lower() in tag_fragments:
                    return chapter_name

    return None


def get_build_variants(selected_chapter: str) -> List[str]:
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
args = parser.parse_args()

force_download = args.force_download

# Get chapter name from git tag if "github_actions" specified as the chapter
chapter_name = args.chapter
if chapter_name == "github_actions":
    chapter_name = get_chapter_name_from_git_tag()
    if chapter_name is None:
        print(
            f">>>> WARNING: No chapter name (or 'all') was found in git tag {GIT_TAG} - skipping building .assets"
        )
        exit(0)

# Get a list of build variants (like 'onikakushi 5.2.2f1 win') depending on commmand line arguments
build_variants = get_build_variants(chapter_name)
print(f"For chapter '{chapter_name}' building: {build_variants}")

# Install python dependencies
print("Installing python dependencies")
call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Download and extract the vanilla assets
assets_path = "assets"
vanilla_archive = "vanilla.7z"
vanilla_folder_path = os.path.join(assets_path, "vanilla")
vanilla_fully_extracted = os.path.exists(vanilla_folder_path) and not os.path.exists(vanilla_archive)
if force_download or not vanilla_fully_extracted:
    print("Downloading and Extracting Vanilla assets")
    pathlib.Path(vanilla_archive).unlink(missing_ok=True)
    if os.path.exists(vanilla_folder_path):
        shutil.rmtree(vanilla_folder_path)

    download("http://07th-mod.com/archive/vanilla.7z")
    seven_zip_extract(vanilla_archive)

    # Remove the archive to indicate extraction was successful
    pathlib.Path(vanilla_archive).unlink(missing_ok=True)
else:
    print("Vanilla archive already extracted - skipping")

# Download and extract UABE
uabe_folder = "64bit"
uabe_archive = "AssetsBundleExtractor_2.2stabled_64bit_with_VC2010.zip"
uabe_fully_extracted = os.path.exists(uabe_folder) and not os.path.exists(uabe_archive)
if force_download or not uabe_fully_extracted:
    print("Downloading and Extracting UABE")
    pathlib.Path(uabe_archive).unlink(missing_ok=True)
    if os.path.exists(uabe_folder):
        shutil.rmtree(uabe_folder)

    # The default Windows github runner doesn't have the 2010 VC++ redistributable preventing UABE from running
    # This zip file bundles the required DLLs (msvcr100.dll & msvcp100.dll) so it's not required
    download(f"http://07th-mod.com/archive/{uabe_archive}")
    seven_zip_extract(uabe_archive)

    # Remove the archive to indicate extraction was successful
    pathlib.Path(uabe_archive).unlink(missing_ok=True)
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
for command in build_variants:
    print(f"Building .assets for {command}...")
    if working_cargo:
        call(f"cargo run {command}")
    else:
        call(f"ui-compiler.exe {command}")
