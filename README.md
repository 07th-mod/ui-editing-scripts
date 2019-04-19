UI Compiler
----

Scripts for easier editing of Unity assets for Higurashi.

To use this tool you will need to install both Python and Rust.

Next you will need to download the [vanilla UIs](http://07th-mod.com/higurashi_resources/vanilla.7z) for Higurashi games and unpack them into `assets/vanilla`.

You'll also need UABE 2.2 stable or newer (or 2.2 beta4 with [this patch applied](https://github.com/DerPopo/UABE/files/2408196/AssetsBundleExtractor_2.2beta4_applyemip.zip)) and 7zip command line executable. Both `AssetBundleExtractor.exe` and `7za.exe` need to be available in your system `PATH`.

Then simply run this:

```
cargo run <chapter> <platform> <system>
```

`<chapter>` is simply `onikakushi`, `watanagashi` and so on.

`<platform>` is `steam`, `mg` or `gog`.

`<system>` is `win` or `unix`.

Documentation for the underlying python scripts can be found [here](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).

The rust script will generate a new emip file, apply it to the assets and pack the assets into 7zip archive we need for a release.

If you want to use this tool to compile assets for a different language, you can change the files in the assets directory to your needs.
