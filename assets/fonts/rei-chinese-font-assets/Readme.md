Font objects for Rei (Ch.9) for Chinese

See scripts\CharacterInfoExtraction\msgothic_2_charset_ZH_and_JP.txt

Texture is 4096x8192 resolution

## Material edits to fix font weight and outline

To fix the font weight and outline, I copied the material settings from my build Unity project and modified the material:
- "_WeightNormal" was 0 in vanilla, now set to 0.75 (equivalent to 'bold')
- "_OutlineWidth" was 0.15 ? in vanilla, now set to 0.2. Unsure if the engine overrides this value
- texture resolution changd from 2048 to 4096, unsure if this changes anything
- various settings copied from built unity project, unsure if they do anything

## Charset Used

Translator supplied 'commonly used 7000 characters', which I merged with JP charset to get `msgothic_2_charset_ZH_and_JP.txt` in the `scripts/CharacterInfoExtraction` folder.

## Font Used

"WenQuanYi Micro Hei Mono - Regular"