# UI Compiler

Scripts for easier editing of Unity assets for Higurashi.

The main rust script will generate a new emip file, apply it to the assets and pack the assets into 7zip archive we need for a release.

## Documentation Notes

Please note that documentation is in two places:

1. This Readme.md file
2. [Detailed documentation with images etc. on this repository's Wiki](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).

Please look through the detailed documentation, especially if you're working on a new chapter, new language, or using UABE - this file does not contain information on those topics.

## Prerequisites

To use this tool you will need these prerequisites:

- Install Python 3
- Install the Python package `unitypack` (do `pip install unitypack`)
- Install Rust
- Download the [vanilla UIs](http://07th-mod.com/archive/vanilla.7z) for Higurashi games and unpack them into `assets/vanilla`.
- You'll also need UABE 2.2 stable or newer (or 2.2 beta4 with [this patch applied](https://github.com/DerPopo/UABE/files/2408196/AssetsBundleExtractor_2.2beta4_applyemip.zip))
  - Make sure `AssetBundleExtractor.exe` is on your `PATH`
- You'll need the 7zip command line executable
  - Make sure `7za.exe` is available in your system `PATH`.

## Usage

### Preparation for a new episode

#### Preparing font files

You'll need to extract the 'msgothic' font files from the stock `.assets` file before starting:

1. Open one of the `sharedassets0.assets` from the new episode in UABE
2. Find two font files (search for `*msgothic*` and hit F3 a couple times). Note there are other files with msgothic in the name, you're looking for ~100kb files with the exact names below:
    - `MonoBehaviour msgothic_0 SDF`
    - `MonoBehaviour msgothic_2 SDF`
1. Click "Export Raw" and save the files to disk
2. Rename them as `msgothic_0.dat` and `msgothic_2.dat`
3. Move them to `assets/vanilla/<chapter>/msgothic_0.dat` & `assets/vanilla/<chapter>/msgothic_2.dat`

### Generating sharedassets0.assets

Then simply run this:

```
cargo run <chapter> <unityversion> <system>
```

`<chapter>` is simply `onikakushi`, `watanagashi` and so on.

`<unityversion>` is the unity version, like `5.5.3p3` or `2017.2.5`. Note that for version `2017.2.5f1`, you just enter `2017.2.5` (currently only support the first 8 characters of the unity version)

`<system>` is `win` or `unix`.

## Extra Notes

If you want to use this tool to compile assets for a different language, you can change the files in the assets directory to your needs.

## Developer Notes

Documentation for the underlying python scripts can be found [here](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).
