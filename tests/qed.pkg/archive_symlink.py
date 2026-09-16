#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a local archive rooted at a path spelled through a symbolic link lists its folders:
the filesystem resolves the root when it is mounted, so a request must be resolved the same
way before it is projected onto the root
"""

# externals
import os
import shutil

# support
import qed

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# a scratch tree
actual = os.path.join(here, "archive_symlink_ws")
# a defensive guard against a stale one
if os.path.lexists(actual):
    # start clean
    shutil.rmtree(actual)
# make it, with a folder and a file
os.makedirs(os.path.join(actual, "nested"))
open(os.path.join(actual, "top.dat"), "w").close()
open(os.path.join(actual, "nested", "inner.dat"), "w").close()
# and a symbolic link to it
link = os.path.join(here, "archive_symlink_link")
# a defensive guard against a stale one
if os.path.lexists(link):
    # start clean
    os.remove(link)
os.symlink(actual, link)

# connect the archive through the link
archive = qed.archives.local(name="symlinked", uri=f"file:{link}")
# list its root, addressed through the link as well
entries = archive.contents(uri=qed.primitives.uri.parse(f"file:{link}"))
# the folder and the file are there, folders first
assert [name for name, _, _ in entries] == ["nested", "top.dat"]
# the folder is addressed by its resolved location
_, nested, isFolder = entries[0]
assert isFolder
assert nested == f"file:{os.path.realpath(actual)}/nested"
# and listing it works too
assert [name for name, _, _ in archive.contents(uri=qed.primitives.uri.parse(nested))] == [
    "inner.dat"
]

# the link is not needed any more
os.remove(link)


# end of file
