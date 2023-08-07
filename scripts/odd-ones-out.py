#!/usr/bin/env python3

"""
This script generates the odd-25pct-out.txt level on stdout.
"""

import random

PREAMBLE = \
r'''$BUILT 2023-06-02 01:03:21
$AUTHOR Green Frisbee
$ENGLISH Odd 25% Out

#INTENDED_NUMBER_OF_PLAYERS 1
#SIZE_X 3200
#SIZE_Y 1004
#BACKGROUND_RED 208
#BACKGROUND_GREEN 255
#BACKGROUND_BLUE 0

#INITIAL 999
#REQUIRED 999
#SPAWN_INTERVAL 1

#WALKER 999
#RUNNER 999
#CLIMBER 999
#FLOATER 999
#EXPLODER2 999
#BLOCKER 999
#BUILDER 999
#PLATFORMER 999
#BASHER 999
#MINER 999
#DIGGER 999
#JUMPER 999
#BATTER 999
#CUBER 999
'''

TILE_GROUP = \
r'''$BEGIN_TILE_GROUP 0
:geoo/construction/platformbrick: 0 12
:geoo/construction/platformbrick: 32 0
:geoo/construction/platformbrick: 32 2
:geoo/construction/platformbrick: 32 4
:geoo/construction/platformbrick: 32 6
:geoo/construction/platformbrick: 32 8
:geoo/construction/platformbrick: 32 10
$END_TILE_GROUP
'''

# Width and Height of the the repeated section
W, H = 64, 50
# Number of repetitions per row and per column
# (If Y_REPS were 40, there'd be no floor at the very bottom.)
X_REPS, Y_REPS = 50, 20
assert (X_REPS * Y_REPS == 1000)
# 1000, because 999 is the maximum number of lixes, and instances of a skill, per level

def coin_toss():
    return random.choice((False, True))

def valid_coordinates():
    """
    Generator for (x,y) pairs.

    Each pair identifies an instance of the repeated section.

    These are NOT pixel offsets.
    """
    n = 0
    for i in range(X_REPS):
        for j in range(Y_REPS):
            n += 1
            if n <= 999:
                yield (i, j)

print(PREAMBLE)
print()
for i, j in valid_coordinates():
    print(f":geoo/abstract/hatch.H: {W*i + 0} {H*j + 4}")
print()
for i, j in valid_coordinates():
    print(f":geoo/abstract/goal.G: {W*i + 32} {H*j + -8}")
print()
print(TILE_GROUP)
print()
for i, j in valid_coordinates():
    print(f":Group-0: {W*i + 0} {H*j + 40}")
    if coin_toss() and i > 0: # NOTE: i must be non-zero because first column has no left border
        # Add one platform on the right to make it unclimbable
        print(f":geoo/construction/platformbrick: {W*i + 32} {H*j + 40 - 2}")
    # A given lix will exit if:
    # - first column lixes: always
    # - second column lixes: always (to the right if TAILS, to the left if HEADS)
    # - all other columns: if either left or right is TAILS, i.e., with probability 75%
    #
    # Thus, per run of this script, the average number of lixes to need manual attention will
    # be 25% * (999 - 2*Y_REPS) ≈ 239.75
print(f":raymanni/toys/cracker: {W*(X_REPS-1)} {H*(Y_REPS-1) - 5} r")
print(f":raymanni/toys/cracker: {W*(X_REPS-1)} {H*(Y_REPS-1) + 17} fr")
