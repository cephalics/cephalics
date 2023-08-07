#!/usr/bin/env python3

"""
This script generates the odd-one-out.txt level on stdout.
"""

PREAMBLE = \
r'''$BUILT 2023-06-02 01:03:21
$AUTHOR Green Frisbee
$ENGLISH Odd One Out

#INTENDED_NUMBER_OF_PLAYERS 1
#SIZE_X 3200
#SIZE_Y 1004
#BACKGROUND_RED 255
#BACKGROUND_GREEN 208
#BACKGROUND_BLUE 0

#INITIAL 999
#REQUIRED 999
#SPAWN_INTERVAL 1

#WALKER 1
#RUNNER 1
#CLIMBER 1
#FLOATER 1
#EXPLODER2 1
#BLOCKER 1
#BUILDER 1
#PLATFORMER 1
#BASHER 1
#MINER 1
#DIGGER 1
#JUMPER 1
#BATTER 1
#CUBER 1
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

SECRET = 20*9 - 1 # chosen at random from {Y_REPS+1..999}
#SECRET = 3 # for debugging

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
    if SECRET in { i*Y_REPS + j, (i-1)*Y_REPS + j }:
        # Add one platform on either side to make them both unclimbable
        print(f":geoo/construction/platformbrick: {W*i + 32} {H*j + 40 - 2}")
print(f":raymanni/toys/cracker: {W*(X_REPS-1)} {H*(Y_REPS-1) - 5} r")
print(f":raymanni/toys/cracker: {W*(X_REPS-1)} {H*(Y_REPS-1) + 17} fr")
