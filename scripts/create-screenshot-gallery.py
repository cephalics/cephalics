#!/usr/bin/env python3

"""
A script to generate the screenshots/ hierarchy from the lixdatadir/ hierarchy.

Usage:
    ./scripts/create-screenshot-gallery.py [LEVELFILE_PATH...]

Both hierarchies are assumed to live in CWD.

Dependencies:
    lix(1)
    optipng(1)
    asciidoc(1)
"""

import collections
import functools
import glob
import itertools
import logging
import multiprocessing
import os
import os.path
import shutil
import subprocess
import sys
import tempfile


### Preparations
logging.basicConfig(
    format='create-screenshot-gallery.py:%(lineno)d[%(process)d]@%(funcName)s: %(message)s',
    level=logging.DEBUG,
)

PngAndItsTxt = collections.namedtuple('PngAndItsTxt', 'png txt')

SCREENSHOTS_DIR = 'screenshots'


### Library functions
def name_of_level(levelfile_path):
    "Given filename of a level, return the level's user-facing name."
    return next(
        line.strip().split(' ', 1)[-1]
        for line in open(levelfile_path)
        if line.startswith('$ENGLISH')
    )

# Optimization, to avoid unnecessary syscalls and under-the-hood exceptions
@functools.cache
def _mkdir_only_once(pathname):
    "Like mkdir(), but optimize away the call if it was already done in this run."
    os.makedirs(pathname, exist_ok=True)

def create_png_for(levelfile_path):
    """
    Create a PNG screenshot for the given level
    
    Arguments: path to a level file (.txt)
    Creates: screenshot of that level under SCREENSHOTS_DIR
    Returns: path to screenshot
    """
    assert levelfile_path.endswith('.txt')
    to_dir = os.path.join(SCREENSHOTS_DIR, os.path.dirname(levelfile_path.split('/levels/', 1)[-1]))
    logging.info('Processing %s', levelfile_path)
    _mkdir_only_once(to_dir)
    with tempfile.TemporaryDirectory() as tmphome:
        new_env = os.environ.copy()
        new_env.update(dict(
            HOME=tmphome,
            XDG_DATA_DIRS=
                (os.environ['XDG_DATA_DIRS'] + ':'
                 if 'XDG_DATA_DIRS' in os.environ
                 else '') \
                +
                os.path.abspath('./xdg/share')
        ))
        subprocess.check_call(
            ['lix', '--image', '--', levelfile_path],
            env=new_env,
        )
        created_file = glob.glob(os.path.join(tmphome, '.local/share/lix/export/*'))[0]
        png_path = os.path.join(to_dir, os.path.basename(created_file))
        os.rename(created_file, png_path) # src and dst are probably on the same device (mount point)
    subprocess.check_call(['optipng', '-quiet', '--', png_path])
    return png_path

def generate_index(pngs_and_respective_txts, fp):
    """
    Generate an asciidoc format index for PNGS_CREATED and write it to fp
    (a file-like object).
    """
    emit = functools.partial(print, file=fp)

    # Note asciidoc forbids h4 to follow h2 immediately; an h3 in between is
    # required.  Thus, add headings not only for directories that contain
    # levels, but also for any intermediate ancestor directories thereof.
    headings_needed = []
    @functools.cache
    def _add_heading(subdir):
        parent = os.path.dirname(subdir)
        if parent and parent != SCREENSHOTS_DIR and parent not in headings_needed:
            _add_heading(parent)
        headings_needed.append(subdir)
    for png_and_txt in pngs_and_respective_txts:
        _add_heading(os.path.dirname(png_and_txt.png))

    # Now, prepare a dict mapping dirs to generators of levels within those dirs.
    # The dict only includes dirs that actually have levels.
    grouper = {
        k: list(g)
        for k, g in 
        itertools.groupby(
            pngs_and_respective_txts,
            key = lambda png_and_txt: os.path.dirname(png_and_txt.png),
        )
    }

    def C(subdir):
        "Return a string for the number of levels in SUBDIR"
        return \
        " (%d levels)" % (
            sum(
                len(grouper[key])
                for key in grouper.keys()
                # Given X/foo, match X/foo/, X/foo/bar/, and X/foo/bar/baz/,
                # but not X/fooqux/.
                if f"{key}/".startswith(f"{SCREENSHOTS_DIR}/{subdir}/")
            )
        )

    # Finally, emit output.
    emit('=', 'Cephalics Screenshots')
    #emit(':figure-caption!:')
    emit()
    emit(
        "This document contains screenshots of all levels in Cephalics.",
        "",
        "The levels are grouped by author:",
        "",
        ""
        + "* <<_brown_bear,Brown Bear's levels>>" + C('brown-bear')

        #, "* <<_green_frisbee,Green Frisbee's levels>>" + C('green-frisbee')

        , "* <<_green_frisbee_easy,Green Frisbee's easy levels>>" + C('green-frisbee/easy')
        +   ": levels whose solutions should be readily apparent"

        , "* <<_green_frisbee_regular,Green Frisbee's regular levels>>" + C('green-frisbee/regular')
        +   ": levels that require figuring out how to get to the goal (exit)."

        , "* <<_green_frisbee_unusual,Green Frisbee's unusual levels>>" + C('green-frisbee/unusual')
        +   ": levels that exploit rare game mechanics, "
        +      "or require unusual in-game skills to solve."

        , "* <<_green_frisbee_special,Green Frisbee's special levels>>" + C('green-frisbee/special')
        +   ": levels that might be frustrating were they included in the other subsets"

        , "* <<_green_frisbee_examples,Green Frisbee's example levels>>" + C('green-frisbee/examples')
        +   ": these levels are minimal examples of Lix game mechanics"

        , "* <<_green_frisbee_wip,Green Frisbee's work-in-progress levels>>" + C('green-frisbee/WIP')
        +   ": not-yet-released levels for public testing"

        , "* <<_white_closet,White Closet's levels>>" + C('white-closet')

        , "",
        sep="\n",
    )
    emit()
    for heading in headings_needed:
        heading_relpath = heading.removeprefix(SCREENSHOTS_DIR + '/')
        if '/beware-of/' in heading_relpath:
            continue
        emit('=' * (2+heading_relpath.count(os.path.sep)), heading_relpath)
        emit()
        if heading_relpath.endswith('/beware-of'):
            emit(f"See link:{heading_relpath}/[].")
            emit()
            continue
        lvlno = 0
        for png_and_txt in grouper.get(heading, []):
            lvlno += 1
            png_relpath = png_and_txt.png.removeprefix(SCREENSHOTS_DIR + '/')
            emit(
                f'image::{png_relpath}['
                    f'title={name_of_level(png_and_txt.txt)!r},'
                    f'alt="screenshot of this level",'
                    f'caption="Level {heading_relpath.rstrip("/")}#{lvlno}: ",'
                f']'
            )
            emit()

def sort_pngs_and_respective_txts(pngs_and_respective_txts):
    @functools.cache
    def _order_file_contents_for(subdir):
        fn = os.path.join(subdir, '_order.X.txt')
        try:
            return open(fn).read().splitlines()
        except FileNotFoundError:
            return tuple()
    def _order(subdir, dirent):
        "Return the order of DIRENT within SUBDIR as would be shown in the UI."
        declared_order = _order_file_contents_for(subdir)
        try:
            return (42, declared_order.index(dirent))
        except ValueError: # not in the list
            # Anything not in the list sorts greater than anything in the list
            # (because min(43, 44) > 42), and amongst themselves, directories
            # before files (because 43 < 44).
            #
            # ### It shouldn't matter too much which is 43 and which is 44; the
            # ### groupby() later only cares that all files be together and all
            # ### non-files be together.
            if dirent.endswith('.txt'):
                return (44, dirent)
            else:
                return (43, dirent)

    def _keyfunc(png_and_txt):
        key = []
        ancestor = png_and_txt.txt
        while ancestor:
            ancestor, dirent = os.path.split(ancestor)
            key.append(_order(ancestor, dirent))
        return tuple(reversed(key))
    pngs_and_respective_txts.sort(key = _keyfunc)

def main(argv):
    if not argv:
        argv = glob.glob('lixdatadir/levels/**/*.txt', recursive=True)

    argv = [x for x in argv if not x.endswith('_order.X.txt')]

    ## Create PNG files
    pngs_created = []
    with multiprocessing.Pool() as p:
        pngs_created = p.map(create_png_for, argv)
    # Use sorted() to match in-game order in the output.  (Especially important
    # because the levels are numbered, both in-game and in the output.)
    pngs_and_respective_txts = list(itertools.starmap(PngAndItsTxt, zip(pngs_created, argv)))
    sort_pngs_and_respective_txts(pngs_and_respective_txts)

    ## Create asciidoc index
    readme_path = os.path.join(SCREENSHOTS_DIR, 'README.asciidoc')
    generate_index(pngs_and_respective_txts, open(readme_path, 'w'))

    ## Compile it
    logging.info('Compiling .asciidoc to .html')
    subprocess.check_call(['asciidoc', '--', readme_path])

### Parse argv
if __name__ == '__main__':
    main(sys.argv[1:])
