# UI Compiler

Scripts for easier editing of Unity assets for Higurashi.

The main rust script will generate a new emip file, apply it to the assets and pack the assets into 7zip archive we need for a release.

## Documentation Notes

Please note that documentation is in two places:

1. This Readme.md file (for basic usage information)
2. [Detailed documentation with images etc. on the `higurashi-dev-guides` Wiki](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).
    - You don't need to read all of this to use the tool!

----

## Usage instructions for translators and dev team

### Prerequisites

1. Install Python 3
2. Run `pip install numpy Pillow unitypack` to install the required Python packages
3. Install Rust
4. Download exactly this version of UABE https://github.com/SeriousCache/UABE/releases/tag/2.2stabled
5. Download 7zip (standalone console version) from here https://www.7-zip.org/download.html
6. Extract UABE and 7z and make sure **both** are on your `PATH`
   - On Windows, you need to restart your terminal window to update your `PATH`.
     - Try caling `AssetBundleExtractor.exe`
     - Try caling `7za.exe`
7. Download the [vanilla UI archive](http://07th-mod.com/archive/vanilla.7z) and unpack it into the repository root (creating the folder `assets/vanilla`).

### Using the tool to generate sharedassets0.assets

To build all chapters:
 - On Linux open a terminal and run the below command
 - On Windows with "Git for Windows" installed, right click the folder and click "Git Bash Here", then use that terminal

```
./compileall.sh
```

To build a particular chapter/version run the following command

```
cargo run <chapter> <unityversion> <system>
```

`<chapter>` is simply `onikakushi`, `watanagashi` and so on.

`<unityversion>` is the unity version, like `5.5.3p3` or `2017.2.5`. Note that for version `2017.2.5f1`, you just enter `2017.2.5` (currently only support the first 8 characters of the unity version)

`<system>` is `win` or `unix`.

----

## Usage instructions when preparing for a new episode

The following information is only used when generating a new episode.

Please look through the detailed documentation, especially if you're working on a new chapter, new language, or using UABE - this file does not contain information on those topics.

### Preparing font files

You'll need to extract the 'msgothic' font files from the stock `.assets` file before starting:

1. Open one of the `sharedassets0.assets` from the new episode in UABE
2. Find two font files (search for `*msgothic*` and hit F3 a couple times). Note there are other files with msgothic in the name, you're looking for ~100kb files with the exact names below:
    - `MonoBehaviour msgothic_0 SDF`
    - `MonoBehaviour msgothic_2 SDF`
1. Click "Export Raw" and save the files to disk
2. Rename them as `msgothic_0.dat` and `msgothic_2.dat`
3. Move them to `assets/vanilla/<chapter>/msgothic_0.dat` & `assets/vanilla/<chapter>/msgothic_2.dat`


## Extra Notes

If you want to use this tool to compile assets for a different language, you can change the files in the assets directory to your needs.

## Developer Notes

Documentation for the underlying python scripts can be found [here](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).
