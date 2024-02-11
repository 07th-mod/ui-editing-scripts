from pathlib import Path
import re

def load_existing_list(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read()

japanese_list = '../test.txt'
multilang_list = '../msgothic_2_charset_OtherLang.txt'
out_char_list = '../out.txt'

jp = load_existing_list(japanese_list)
multi = load_existing_list(multilang_list)

all_chars = set(jp) | set(multi)

all_chars = sorted(list(all_chars))

with open(out_char_list, 'w', encoding='utf-8', newline='') as f:
    for c in all_chars:
        f.write(c)
