# Fonts

To avoid confusion in this readme:
- "font asset" will refer to the font asset used in the Unity Sharedassets files.
- "font file" will refer to what we usually think of as fonts, eg "MS Gothic.ttf" and "PT Sans.ttf"

## Differences between Ch.1-9 and Ch.10 (Hou+)

There are two different font assets inside the vanilla sharedassets for Chapters 1-9:
- `msgothic_0`, which is used for Japanese
- `msgothic_2`, which is used for English

However, chapter 10 only uses one font asset, `msgothic_2`, for both languages.

## Which font files to use when generating assets

We currently keep three fonts in this repository:
- MS-Gothic.ttf: This is used when generating Japanese font assets (`msgothic_0`, except for Hou+).
    - Based off MS Gothic
- PTSans+MS-PGothic.ttf, used for our normal English font assets used in the mod (`msgothic_2`).
    - This is the 'normal' font used in our mod.
    - Based off PTSans, but because even in English mode sometimes we need to display Japanese characters, Japanese characters were filled in using MS Gothic.
- DejaVuSans+MS-PGothic.ttf, used for translations which require special characters like Vietnamese (`msgothic_2`)
    - Mainly used for translators (as it supports more languages)
    - Based off DejaVuSans which supports even more non-english characters.
    - Looks visually different to PTSans

## Supporting more characters

### For Chapters 1-8

If you're developing a translation into a non-English language like Vietnamese and you find that the font is missing characters needed for your language, try renaming the two ``msgothic_2` for non-English` files over the PT Sans ones. These are based off of Deja-Vu Sans which has support for more languages than PT Sans does.

### For Chapters 9 (Rei) and 10 (Hou+)

There may be some alternative fonts in the `assets\files-rei` and `assets\files-hou-plus`, if not contact the mod team to see if they can be added.

## Hou Plus Notes

Hou Plus uses a single font file (`msgothic_2`). You will need to use the 'combined' list which contains both 'OtherLang' and Japanese characters, if you want to generate your own fonts

## Chinese Font Notes

For Chinese, Noto Sans SC seems to cover all characters, but ask the translation team which font they wish to use in case they have a preferred one.

Noto Sans SC: https://fonts.google.com/noto/specimen/Noto+Sans+SC

One team used "WenQuanYi Micro Hei Mono - Regular"