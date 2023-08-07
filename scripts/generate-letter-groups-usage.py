#!/usr/bin/env python3

"""
SYNOPSIS:

     generate-letter-groups-usage.py LOREM [IPSUM [DOLOR [SIT [AMET...]]]] >> levels/green-frisbee/font-test-SUBSET.txt

This script emits to stdout a Lix level excerpt.

The excerpt, if appended to a level that has the named terrain groups for letters
already defined, will add to the level, at (0,0), terrain forming a Latin-script
message.

The message is taken from argv, joined by spaces.

The message may comprise the characters <ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?> and
space.  Case is ignored.

The named terrain groups for letters should be copied from font-test-SUBSET.txt
and added to the level as well as (and, I guess, before) the output of this script.
"""

import logging
import string
import sys
import uuid

if sys.argv[1:] and sys.argv[1].startswith('-'):
    sys.exit(__doc__)

#logging.getLogger().setLevel(logging.DEBUG)

ALPHABET = string.ascii_lowercase[:] + string.digits + '?'
WIDTHs = dict(
    # TODO: derive all magic numbers from levels/green-frisbee/font-test-SUBSET.txt
    i=1,
    j=2,
    k=4,
    p=2,
    q=2,
    r=2,
    v=2,
    y=2,
    # TODO extend with values for digits and question mark
)
ATOM_WIDTH_px = 8
TAIL_WIDTH_px = 4

# TODO add support for digits and question mark
def width(letter):
    assert letter in ALPHABET
    return WIDTHs.get(letter, 3)

# TODO add support for digits and question mark
def has_tail(letter):
    assert letter in ALPHABET
    return (letter in 'qr')

added_group_name = 'latin-message-' + str(uuid.uuid4())
print(f'$BEGIN_TILE_GROUP {added_group_name}')
x_offset = y_offset = 0
for letter in ' '.join(sys.argv[1:]):
    letter = letter.lower()
    if letter == ' ':
        x_offset += ATOM_WIDTH_px
        continue
    group_name = \
        f'letter-{letter.upper()}-red' if letter in string.ascii_lowercase else \
        f'digit-{letter}-red' if letter in string.digits else \
        f'symbol-qmark-red' if letter in '?' else \
        None
    assert group_name
    print(f":Group-{group_name}: {x_offset} {y_offset}")
    x_offset += ATOM_WIDTH_px * width(letter)
    x_offset += TAIL_WIDTH_px * has_tail(letter)
print('$END_TILE_GROUP')
print(f':Group-{added_group_name}: 0 0')
