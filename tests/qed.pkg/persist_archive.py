#! /usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that archives get into the configuration files when the user says so, and at no other
time: connecting, expanding, and collapsing write nothing; saving an archive writes that
archive and no other; the first list of archives to be written reproduces what was attached at
boot, so that making it changes nothing the user did not ask to change; and disconnecting an
archive, including the one the application attaches by default, makes it stay away

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "persist_archive_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it, with a couple of folders to turn into archives
os.makedirs(os.path.join(workspace, "one", "inner"))
os.makedirs(os.path.join(workspace, "two"))
# their locations
one = f"file:{os.path.realpath(os.path.join(workspace, 'one'))}"
two = f"file:{os.path.realpath(os.path.join(workspace, 'two'))}"

# the configuration file says nothing about archives, so the application attaches its default
original = "# -*- pyre -*-\n\n# nothing to see here\n\n# end of file\n"
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
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store


# the text of the configuration file
def text():
    # read it
    with open("qed.yaml", mode="r", encoding="utf-8") as stream:
        # all at once
        return stream.read()


# the document in the configuration file
def doc():
    # load it
    return pyre.config.newYamlEditor(uri="qed.yaml")


# boot attached the archive over the current directory, and nothing else
assert store.bootArchives == {"local:workspace"}
# it says what the configuration says, which is nothing, so there is nothing to save
assert next(iter(store.archives)).dirty is False

# connect two archives, and put a couple of folders on display
first = store.connectArchive(archive=qed.archives.local(name="first", uri=one))
second = store.connectArchive(archive=qed.archives.local(name="second", uri=two))
store.expandFolder(archive=one, uri=one)
store.expandFolder(archive=one, uri=f"{one}/inner")
store.expandFolder(archive=two, uri=two)
store.collapseFolder(archive=two, uri=two)
# none of which wrote anything
assert text() == original
# an archive that the session made has never been saved, so it has something to save
assert first.dirty is True
assert second.dirty is True

# save the first one
assert store.persistArchive(uri=one) is first
# it has a section, with what is on display
saved = doc()
assert saved.get("first", "uri") == one
assert list(saved.get("first", "expanded")) == [one, f"{one}/inner"]
# the list that attaches it was made, and it names what boot attached, so the archive over
# the current directory does not disappear as a side effect, followed by the one just saved
assert list(saved.get("archives")) == [
    "qed.archives.local#local:workspace",
    "qed.archives.local#first",
]
# the other archive of the session is nowhere to be found
assert saved.get("second") is None
assert "second" not in text()

# the archive now says what the file says
assert first.dirty is False
# and the other one still has something to save
assert second.dirty is True

# saving it again changes nothing
before = text()
store.persistArchive(uri=one)
assert text() == before

# take a folder off display; the file does not follow until the user says so
store.collapseFolder(archive=one, uri=f"{one}/inner")
assert text() == before
# so there is something to save
assert first.dirty is True
# putting the folder back brings the archive in line with the file again, with nothing saved:
# what matters is whether a save would change anything, not whether something happened
store.expandFolder(archive=one, uri=f"{one}/inner")
assert first.dirty is False
# take it off again, and save this time
store.collapseFolder(archive=one, uri=f"{one}/inner")
store.persistArchive(uri=one)
assert list(doc().get("first", "expanded")) == [one]
assert first.dirty is False

# disconnect the archive that was never saved; the files never knew about it
before = text()
store.disconnectArchive(uri=two)
assert text() == before

# disconnect the archive over the current directory; it has no section anywhere, and it stays
# away because the list leaves it out
workdir = next(a for a in store.archives if a.pyre_name == "local:workspace")
store.disconnectArchive(uri=str(workdir.uri))
assert list(doc().get("archives")) == ["qed.archives.local#first"]

# disconnect the one that was saved; its entry goes, and so does its section, since it lives
# in the workspace file
store.disconnectArchive(uri=one)
final = doc()
assert final.get("first") is None
# the list is empty, and it stays: without it the default archive would be back
assert list(final.get("archives")) == []
assert "archives: []" in text()

# clean up
os.chdir(here)
shutil.rmtree(workspace)


# end of file
