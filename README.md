# UI Compiler

Scripts for easier editing of Unity assets for Higurashi.

The main rust script will generate a new emip file, apply it to the assets and pack the assets into 7zip archive we need for a release.

## Documentation Notes

Please note that documentation is in two places:

1. This Readme.md file (for basic usage information)
2. [Detailed documentation with images etc. on our Wiki](https://07th-mod.com/wiki/developer/sharedassets/ui-editing-scripts/).
    - You don't need to read all of this to use the tool!

----

## Instructions for Translators

Overall, the workflow for translators is:

1. Setup your computer to run our tool, including cloning or forking this repo
2. Modify/replace the files in the repo with your translated versions
3. Run our tool to generate the `.assets` and `.languageSpecificAssets` files you can include in your release

Please continue with detailed instructions below.

### Setup (Windows Only)

The below instructions only work on Windows!

1. Follow [the instructions here](https://phoenixnap.com/kb/how-to-install-python-3-windows) to install Python 3, and make sure Python is on your path
     - If the above link doesn't work, just make sure you do the following:
     - During the install, make sure you tick the checkbox "Add Python 3 to PATH"
     - After the install is finished, **open a fresh command window**, then type `python` to check if python is correctly on your path (should display the python prompt)
2. For translators, fork this repository ([Github forking instructions]( https://docs.github.com/en/get-started/quickstart/fork-a-repo))
     - A fork is recommended for translators as you can check in your changes to github. It also allows you to use Github for building and hosting assets
3. Clone the repository (either this repository, or the one you forked) to your computer

### Modifying images, text, and fonts

#### To modify images

To modify images, replace the image files in the `assets/images` folder.

Folder info:

- `images/shared`: images common to all chapters
- `images/question_arcs`: images specific to chapters 1-4
- `images/answer_arcs`: images specific to chapters 5-8
- `images/specific/[CHAPTER_NAME]`: images specific to a particular chapter
- `images/version-specific/[CHAPTER_NAME]`: images specific to a particular chapter + unity version combo

Make sure have a quick look at all the folders before starting work, so you don't miss any images by accident.

#### To modify text

The game contains various text which is not contained in the game script or the DLL (it is stored directly in the .assets file). This text is also not stored as image files, so you can't edit an image to change it.

To edit these text files, edit the `assets/text-edits.json` file. **Please read <https://07th-mod.com/wiki/developer/sharedassets/ui-editing-scripts/#unitytextmodifier> for more details on how to edit this file.**

#### To modify fonts

To modify fonts, see
 - For Chapters 1-8: <https://07th-mod.com/wiki/developer/sharedassets/ui-editing-scripts/#adding-font-support-for-a-new-language-chapters-1-8-only>
    - Note: Due to some Unity plugins being no longer supported, you may have trouble following these instructions. Please let us know if you have problems and we'll try to sort it out.
 - For Chapter 9 <https://07th-mod.com/wiki/developer/sharedassets/ui-editing-scripts/#adding-font-support-for-a-new-language-higurashi-rei-onwards-only>

Fonts are stored in the `assets/fonts` folder as `*.dat` files, with the exception of Rei where fonts are stored in the `assets/files-2019.4` folder.

#### To modify other files

The `assets/files-[UNITY_VERSION]` folders contain files applied to a particular Unity version, regardless of chapter. You normally don't need to modify these files.

Currently these folders contain higher quality caret sprites (the little cursor/triangle displayed at the end of a text line), with the exception of the `assets/files-2019.4` folder which also contains fonts for Higurashi Rei.

### Generating .assets and .languageSpecificAssets files (Windows Only)

To list the supported Higurashi chapters for this tool, run

```python build.py```

which should show an error message and list available chapters

Then run

```python build.py onikakushi```

Then the output files will be located in the `output/translation` folder. You can then merge the `HigurashiEp0X_Data` folder with the one in your release. **Please include all the files (not just the `sharedassets0.assets` file), so the installer can select the correct file at install time.**

If you want to rebuild all chapters, run `python build.py all` to build all chapters.

### Common Problems

You may encounter the following problems:
- Windows Defender may block/delete our precompiled `ui-compiler.exe`. In this case, you can either try to unblock it, or install Rust to make the script compile it on your own computer. Contact us if you have this issue.
- For any other error, likely we just need to update the build script, so please contact us.

### Updating dependencies

**NOTE: The script should automatically detect if the vanilla assets or UABE has changed, and re-download them. But if that doesn't work, use the '--force-download' option like so:**

```python build.py rei --force-download```

## Instructions for Dev Team

Instructions are the same as for translators, but archive files will be automatically created in the `output` folder

----

## Modifying Assets

Assets are located in the `assets` folder. Replace any file in the `assets` folder, then run the script again, and it should be included in the generated assets files.

### Building assets using Github Actions

#### Note for forks/translators

Github actions might be disabled for your forks. Clicking on the 'Actions' tab should allow you to enable it. Please do this before proceeding.

----

## Triggering Github Actions Builds

### Building a release

To use Github Actions to build a release, create a tag like `v1.0.6_onikakushi` which contains the chapter name (separated by an underscore) you want to build (or 'all' for all chapters).

Click on the 'Actions' tab to observe the build process.

Once the build is complete, go to the 'Releases' page, and a new draft release should appear. You can check everything is OK before publishing the release, or just download the files without publishing the release.

Note that doing this will build both the `translation.7z` file for translators to use, and also the individual archives for the 07th-mod developers to use.

### Building `ui-compiler.exe` using Github Actions

To build just the `ui-compiler.exe` using Github Actions (on Github's server), push any tag to the repository.

----

## New Episode Preperation Instructions

The following information is only used when adding support for a new episode.

Please look through the detailed documentation, especially if you're working on a new chapter, new language, or using UABE - this file does not contain information on those topics.

### WARNING about Unix/MacOS `sharedassets0.assets`

We've found that the MacOS sharedassets can be used on Linux, **but the Linux sharedassets CANNOT be used on MacOS in certain cases**, giving you the "purple text" issue.

For this reason, whenever a new chapter is prepared, the 'vanilla' unix `sharedassets0.assets` should be taken from the MacOS version.

### Initial dumping of textures

You will initially want to inspect all the textures in the UI file to see if any new images need to be added to the `assets/images/*` folders.

1. Open and select the `sharedassets0.assets` from the new episode in UABE
2. Click the "Type" column to sort by "Type"
3. Scroll down until you see "Texture2D"
4. Hold shift, then click the first "Texture2D" item
5. Continue holding shift, then click the last "Texture2D" item. This should highlight all the "Texture2D" items.
6. On the right hand side, click "Plugins"->"Export to .png"

The textures will be dumped as images in the selected folder. However please note:

1. You will need to rename them by keeping the first part of the name only - for example `ChapterPreview-sharedassets0.assets-27.png` becomes `ChapterPreview.png`
2. It is also possible to use the number (Path ID), but usually you won't do this. In the above example, rename as `27_ChapterPreview.png` (the part after the number is not used, only to describe the file for humans)
3. Make sure you put them in the right subfolder in `assets/images`, refer to "To modify images" section for details

### Preparing font files

You'll need to extract the 'msgothic' font files from the stock `.assets` file before starting:

1. Open one of the `sharedassets0.assets` from the new episode in UABE
2. Find two font files (search for `*msgothic*` and hit F3 a couple times). Note there are other files with msgothic in the name, you're looking for ~100kb files with the exact names below:
    - `MonoBehaviour msgothic_0 SDF`
    - `MonoBehaviour msgothic_2 SDF`
1. Click "Export Raw" and save the files to disk
2. Rename them as `msgothic_0.dat` and `msgothic_2.dat`
3. Move them to `assets/vanilla/<chapter>/msgothic_0.dat` & `assets/vanilla/<chapter>/msgothic_2.dat`

----

## Extra Notes

If you want to use this tool to compile assets for a different language, you can change the files in the assets directory to your needs.

## Developer Notes

Documentation for the underlying python scripts can be found [here](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).

----

## Manual Setup and Running Instructions (Windows Only)

We suggest using the above `python` script intead to setup everything, but these instructions remain here for reference.

These instructions do not rely on the `build.py` script, and are roughly how we ran the `ui-editing-scripts` before the `build.py` was created.

Note: these are rough instructions only, and may need updating.

1. Install Python 3
2. Run `python -m pip install -r requirements.txt` (or `python3` instead of `python`), to install the python dependencies
3. Download [the vanilla assets from our website](http://07th-mod.com/archive/vanilla.7z), then extract them to the root of the repository (the `assets` folder in the archive will merge with the `assets` file in the repository)
4. Download and extract UABE somewhere, then make sure `AssetBundleExtractor.exe` is on your path
5. Decide whether you want to get the pre-compiled executable, or compile the executable yourself (see below):

### Option 1: Getting the pre-compiled executable

1. Download the [pre-compiled `ui-compiler.exe`](https://github.com/07th-mod/ui-editing-scripts/releases/latest/download/ui-compiler.exe)
2. Make sure it is on your path, or in the root of the repository

### Option 2: Compiling the exe yourself

1. [Follow this guide to install Rust on Windows](https://docs.microsoft.com/en-us/windows/dev-environment/rust/setup) There are some gotchas for Windows (like you need to install Visual Studio before installing rust).
2. In the root of the repository, run `cargo build` to check everything works correctly.

## Running ui-editor-scripts

- To compile a particular chapter/variant, open `build.py` and look at the valid chapters, for example:
    - `onikakushi 5.2.2f1`
    - `matsuribayashi 2017.2.5 unix 51100D6D`
- Run `cargo run` (compile yourself) or `ui-compiler` (pre-compiled) with the command you chose earlier. Following the previous example:
    - `cargo run onikakushi 5.2.2f1`
    - `cargo run matsuribayashi 2017.2.5 unix 51100D6D`

If you compiled the exe yourself, you can run the `./compileall.sh` under windows by using `git bash` which comes with Git for Windows.
