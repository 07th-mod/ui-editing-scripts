# Use this script to merge together multiple text-edits.json files together
# It expects all .json files to be in a folder called 'text-edits' next to this script
# It outputs to a file called merged-translations.json
# Files will be output in alphabetical order, so it is recommended to prepend each file with the chapter number
# If there are any conflicts, and exception will be raised.
#
# This script is usually never needed, unless translators have been swapping out the text-edits.json for each chapter
# rather than maintaining a common text-edits.json for all chapters.

import os
import json


class Fragment:
    order = 0

    def __init__(self, fragment_as_dictionary: dict[str, str], en_mode: bool):
        self.current_english = fragment_as_dictionary['CurrentEnglish']
        self.current_japanese = fragment_as_dictionary['CurrentJapanese']

        # When producing the "English" example .json, the 'new' fields should match the 'current' fields
        # as no modification of the text is being performed.
        if en_mode:
            self.new_english = self.current_english
            self.new_japanese = self.current_japanese
        else:
            self.new_english = fragment_as_dictionary['NewEnglish']
            self.new_japanese = fragment_as_dictionary['NewJapanese']

        self.discriminator = fragment_as_dictionary.get('Discriminator')
        self.comment = fragment_as_dictionary.get('Comment')
        self.order = Fragment.order
        Fragment.order += 1

        # Generate a key for this Fragment, used later to check for conflicting fragments
        self.key = self.current_english + self.current_japanese
        if self.discriminator is not None:
            self.key += str(self.discriminator)


    def equals(self, other: 'Fragment'):
        return (
            self.current_english == other.current_english and
            self.current_japanese == other.current_japanese and
            self.discriminator == other.discriminator
        )

    def __repr__(self) -> str:
        return f"{self.order} ce: {self.current_english} cj: {self.current_japanese} ne: {self.new_english} nj: {self.new_japanese} d: {self.discriminator}"

    def as_dict(self):
        retval = {
            'CurrentEnglish': self.current_english,
            'CurrentJapanese': self.current_japanese,
            'NewEnglish': self.new_english,
            'NewJapanese': self.new_japanese,
        }

        if self.discriminator is not None:
            retval['Discriminator'] = self.discriminator

        if self.comment is not None:
            retval['Comment'] = self.comment

        return retval

def merge(all_translations: dict[str, Fragment], fragment: Fragment):

    if not fragment.key in all_translations:
        all_translations[fragment.key] = fragment
    else:
        existing_item = all_translations[fragment.key]

        if existing_item.equals(fragment):
            print(f"Skipping duplicate item {fragment}")
        else:
            raise Exception(f"Warning: non duplicate item existing:{existing_item} new: {fragment}")

en_mode = False

in_folder = "text-edits"

files = os.listdir(in_folder)

all_fragments = [] # type: list[Fragment]

for filename in files:
    path = os.path.join(in_folder, filename)
    print(f"Parsing {path}")

    with open(path, encoding='utf-8') as f:
        chapter_list_dict = json.loads(f.read())

        all_fragments.extend(Fragment(f, en_mode) for f in chapter_list_dict)

all_translations = {}

# Merge all fragments into one dict, ignoring duplicates
for f in all_fragments:
    print(f.current_english)
    merge(all_translations, f)
    print()

# Convert to list and sort by 'order' which is the order the fragments were loaded
sorted_translations = list(sorted(all_translations.values(), key=lambda f: f.order))
for item in sorted_translations:
    print(item)

with open("merged-translations.json", 'w', encoding='utf-8') as out:
    out.write(json.dumps([f.as_dict() for f in sorted_translations], indent=4, ensure_ascii=False))