UI Compiler
----

Scripts for easier editing of Unity assets for Higurashi.

To use this tool you will need to install both Python and Rust. Then simply run this:

```
cargo run <chapter> <platform>
```

`<chapter>` is simply `onikakushi`, `watanagashi` and so on.

`<platform>` is `win` or `mac`. For tatarigoroshi platform can also be `win-mg` and `mac-mg`.

Documentation for the underlying python scripts can be found [here](https://github.com/07th-mod/higurashi-dev-guides/wiki/UI-editing-scripts).

The rust script will generate a new emip file in the output directory which you can apply to assets file using UABE as described in the docs for the python scripts.

If you want to use this tool to compile assets for a different language, you can change the files in the assets directory to your needs.
