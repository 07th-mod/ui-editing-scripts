from pathlib import Path
import re

en_regex = re.compile(r'OutputLine\([^,]*,\s*[^,]*,\s*[^,]*,\s*([^,]*)')

def load_existing_list(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read()


existing_char_list = Path('C:/drojf/large_projects/umineko/ui-editing-scripts/scripts/CharacterInfoExtraction/msgothic_2_charset_OtherLang.txt')
out_char_list = existing_char_list.with_suffix(existing_char_list.suffix + '.out')
source_directory = Path('C:/drojf/large_projects/umineko/HIGURASHI_REPOS')

existing_char_list_text = load_existing_list(existing_char_list)
existing_font_set = set(existing_char_list_text)

all_chars = set()

for file in source_directory.rglob("*.txt"):
    print(file)
    with open(file, encoding='utf-8') as f:
        whole_file_string = f.read()
        for match in en_regex.finditer(whole_file_string):
            if match:
                outputline_english_arg = match.group(1)
                for c in outputline_english_arg:
                    all_chars.add(c)

all_chars_list = list(all_chars)
all_chars_list.sort()

chars_to_add = []
new_char_found = False
for char in all_chars_list:
    if char not in existing_font_set:
        print(f'NEW CHAR: {char}')
        new_char_found = True
        chars_to_add.append(char)

if not new_char_found:
    print("No new characters found!")

final_list = list(existing_font_set.union(all_chars))
final_list.sort()

for c in final_list:
    print(c, end='')

print()


with open(out_char_list, 'w', encoding='utf-8', newline='') as f:
    for i, c in enumerate(existing_char_list_text):
        f.write(c)

        # This is very bad for performance if there are lots of new chars found, but it works for now to maintain ordering
        for new_character in chars_to_add:
            if new_character < c:
                f.write(new_character)
                chars_to_add.remove(new_character)
                print(f"Inserting new character {new_character} at position {i} as it is less than {c}")

if chars_to_add:
    raise Exception(f"One or more characters were not added {chars_to_add}")