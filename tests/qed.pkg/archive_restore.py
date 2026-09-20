#! /usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the store brings back the tree of an archive from the record an earlier session
left behind, and that it treats that record as a claim rather than a fact: the folders that
are still there come back with their contents, the ones that have vanished since are pruned
from the tree and from the configuration file, and a folder that merely could not be listed
is left alone

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "archive_restore_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# the archive lives inside it; build the part of its tree that still exists
root = os.path.realpath(os.path.join(workspace, "data"))
os.makedirs(os.path.join(root, "kept", "deeper"))
os.makedirs(os.path.join(root, "idle"))
# with something to find at the bottom
open(os.path.join(root, "kept", "deeper", "product.dat"), mode="w").close()


# the location of a folder of the archive
def at(*names):
    # as the archive spells it
    return "/".join((f"file:{root}",) + names)


# the record of an earlier session: the root, a branch that is still there, two levels deep,
# a branch that has vanished along with what was open beneath it, and a folder that was never
# part of this archive
recorded = [
    at(),
    at("kept"),
    at("kept", "deeper"),
    at("gone"),
    at("gone", "beneath"),
    at("kept", "vanished"),
    "file:/somewhere/else/entirely",
]
# write the configuration file
with open(os.path.join(workspace, "qed.yaml"), mode="w", encoding="utf-8") as stream:
    # the archive, with its record
    stream.write("# -*- pyre -*-\n\n# the archive\nrestored:\n")
    stream.write(f"    uri: {at()}\n    expanded:\n")
    stream.write("".join(f"        - {folder}\n" for folder in recorded))
    # and the list that attaches it
    stream.write("\n# attach it\narchives:\n    - qed.archives.local#restored\n\n# end of file\n")

# work out of the scratch workspace, so its configuration file is the one that loads
os.chdir(workspace)

# support
import journal
import pyre
import qed

# the store narrates what it prunes, and complains about the folder this driver makes
# unreadable on purpose; both are expected here
journal.info("qed.ux.archives").deactivate()
journal.warning("qed.ux.archives").deactivate()

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the store
store = ux.store
# no fleet is attached, so listings run here, and the whole restoration happens inline
assert store.fleet is None
# find the archive
archive = store.archive(uri=at())
# it came up with the record of the earlier session, and nothing to show for it
assert list(archive.expanded) == recorded
assert list(archive.items()) == []

# bring the tree back
assert store.restoreArchives() is True

# the folders that are still there are on display, in the order they were recorded; the ones
# that vanished are gone, along with what was open beneath them, and so is the stranger
assert list(archive.expanded) == [at(), at("kept"), at("kept", "deeper")]
# and every one of them has its listing, all the way down
assert archive.listing(uri=at()) is not None
assert archive.listing(uri=at("kept")) is not None
assert archive.listing(uri=at("kept", "deeper")) is not None
# nothing is left under way, and nothing failed
assert not any(archive.isPending(uri=folder) for folder in recorded)
assert not any(archive.failure(uri=folder) for folder in recorded)
# so the tree shows its contents: the two folders of the root, the folder within the branch
# that was open, and the product at the bottom
names = sorted(item["name"] for item in archive.items())
assert names == ["deeper", "idle", "kept", "product.dat"], names
# a folder that exists but was not on display stays closed
assert archive.listing(uri=at("idle")) is None

# the configuration file was corrected as well
doc = pyre.config.newYamlEditor(uri="qed.yaml")
assert list(doc.get("restored", "expanded")) == [at(), at("kept"), at("kept", "deeper")]
# so the archive says what the file says, and there is nothing for the user to save: the
# folders that went were taken out of both
assert archive.dirty is False

# asking again changes nothing
assert store.restoreArchives() is False

# a folder that cannot be listed is not evidence that anything beneath it is gone: take the
# listing of the branch away, make the branch unreadable, and refresh
os.chmod(os.path.join(root, "kept"), 0o000)
# carefully, so the permissions are restored whatever happens
try:
    # list everything on display again
    store.refreshArchive(uri=at())
    # the branch reports its failure
    assert archive.failure(uri=at("kept")) is not None
    # and it is still on display, along with what was open beneath it
    assert at("kept") in archive.expanded
    assert at("kept", "deeper") in archive.expanded
# put things back
finally:
    # so the workspace can be removed
    os.chmod(os.path.join(root, "kept"), 0o755)

# when the branch really does go away
shutil.rmtree(os.path.join(root, "kept"))
# a refresh notices
store.refreshArchive(uri=at())
# and takes it, and what was beneath it, off display
assert list(archive.expanded) == [at()]
# in the configuration file as well
doc = pyre.config.newYamlEditor(uri="qed.yaml")
assert list(doc.get("restored", "expanded")) == [at()]

# clean up
os.chdir(here)
shutil.rmtree(workspace)


# end of file
