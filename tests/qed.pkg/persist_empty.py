#! /usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a list that the session filled and then emptied leaves no trace in the configuration
file: expanding an archive records the folder on display, and collapsing it removes the record,
rather than leaving behind a pair of brackets that says what the next session would assume
anyway. The trip must return the file to its original text

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "persist_empty_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it, along with a folder for the archive to show
os.makedirs(os.path.join(workspace, "data", "products"))
# the location of the archive
root = f"file:{os.path.realpath(os.path.join(workspace, 'data'))}"

# the configuration file: two archives, so that the one under test is followed by a section
# it must stay apart from, and a list that attaches them
original = f"""# -*- pyre -*-

# the archive under test
first:
    uri: {root}

# another one, which nobody touches
second:
    uri: {root}/products

# attach them
archives:
    - qed.archives.local#first
    - qed.archives.local#second

# end of file
"""
# write it
with open(os.path.join(workspace, "qed.yaml"), mode="w", encoding="utf-8") as stream:
    # all at once
    stream.write(original)

# work out of the scratch workspace, so its configuration file is the one that loads
os.chdir(workspace)

# support
import pyre
import qed

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the store
store = ux.store
# no fleet is attached, so listings run here
assert store.fleet is None


# the text of the configuration file
def text():
    # read it
    with open("qed.yaml", mode="r", encoding="utf-8") as stream:
        # all at once
        return stream.read()


# the default workspace archive is attached by code, and the session lists it along with the
# ones from the file; account for it, so the comparison is about the archive under test
store.persist(sources=False, views=False)
baseline = text()
# nothing in there about what is on display, since nothing is
assert "expanded" not in baseline

# put the root of the first archive on display
store.expandFolder(archive=root, uri=root)
# the file records it, within the section of the archive
doc = pyre.config.newYamlEditor(uri="qed.yaml")
assert list(doc.get("first", "expanded")) == [root]
# and says nothing about the archive nobody touched
assert doc.get("second", "expanded") is None

# take it off display again
store.collapseFolder(archive=root, uri=root)
# the record is gone, not emptied
doc = pyre.config.newYamlEditor(uri="qed.yaml")
assert doc.get("first", "expanded") is None
assert "expanded" not in text()
# and the file is back to where it was, to the character
assert text() == baseline, text()

# clean up
os.chdir(here)
shutil.rmtree(workspace)


# end of file
