from pathlib import Path
import re

def load_existing_list(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read()

japanese_list = '../msgothic_0_charset_Japanese.txt'
multilang_list = '../msgothic_2_charset_OtherLang.txt'
out_char_list = '../msgothic_2_charset_JP_and_OtherLang.txt'

jp = load_existing_list(japanese_list)
multi = load_existing_list(multilang_list)

chars_to_add = set(jp)
existing_chars = set(multi)


with open(out_char_list, 'w', encoding='utf-8', newline='') as f:
    for i, c in enumerate(multi):
        f.write(c)

        # This is very bad for performance if there are lots of new chars found, but it works for now to maintain ordering
        remove_list = []
        for new_character in chars_to_add:
            if new_character < c:
                f.write(new_character)
                remove_list.append(new_character)
                print(f"Inserting new character {new_character} at position {i} as it is less than {c}")

        for item in remove_list:
            chars_to_add.remove(item)

    remove_list = []
    for char in chars_to_add:
        if char not in existing_chars:
            f.write(char)
        else:
            print(f"WARNING: character {char} already exists, skipping")
        remove_list.append(char)

    for item in remove_list:
        chars_to_add.remove(item)


if chars_to_add:
    raise Exception(f"One or more characters were not added {chars_to_add}")