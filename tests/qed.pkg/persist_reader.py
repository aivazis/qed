#! /usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that readers get into the configuration files when the user says so, and at no other
time: saving a reader writes that reader and no other; the first list of datasets to be
written reproduces what was attached at boot; and disconnecting a reader makes it stay away,
whether it came from the file or was made by the session

Saving a reader records that it is part of the workspace, and nothing about how it was being
looked at: a reader the session made gets a section that says what it is, spelled the way a
person would, with how to get at its product but never the keys; a reader that came from a
file keeps its section exactly as the user wrote it

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil
import types

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "persist_reader_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it
os.makedirs(workspace)

# the configuration file attaches one reader over the raster in this directory
original = """# -*- pyre -*-

# the location of the rasters
qed.native: ..

# the dataset that boot attaches
booted:
    uri: "{qed.native}/c16.dat"
    shape: 65, 65
    cell: c16

# attach it
datasets:
    - qed.readers.native.flat#booted

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


# boot attached the reader from the file, and nothing else
assert store.bootSources == {"booted"}

# connect two more readers over the same raster, the way the session does
raster = os.path.join(here, "c16.dat")
for name in ("first", "second"):
    # make each one
    reader = qed.readers.native.flat(name=name, uri=f"file:{raster}", shape=(65, 65), cell="c16")
    # and connect it
    store.connectSource(source=reader)
# none of which wrote anything
assert text() == original

# make first contact with the reader that came from the file; this resolves its shape and
# binds its cell, which the session did, not the user
next(source for source in store.sources if source.pyre_name == "booted").open()

# save the first one
assert store.persistSource(name="first").pyre_name == "first"
saved = doc()
# it has a section that says what it is
assert saved.get("first", "uri") == f"file:{raster}"
# with its shape, which the recipe renders as configuration text; it reads back as numbers
assert [int(extent) for extent in saved.get("first", "shape")] == [65, 65]
# and its cell by family, not under the name the framework generated for the instance
assert saved.get("first", "cell") == "qed.datatypes.complex128"
# which is enough to build it again
again = qed.readers.native.flat(
    name="first_again",
    uri=saved.get("first", "uri"),
    shape=[int(extent) for extent in saved.get("first", "shape")],
    cell=saved.get("first", "cell"),
)
assert again.cell.pyre_family() == "qed.datatypes.complex128"
# nothing about how it was being looked at made it into the file
assert "amplitude" not in text()
# and it joined the list the file already had, after the reader that was there
assert list(saved.get("datasets")) == [
    "qed.readers.native.flat#booted",
    "qed.readers.native.flat#first",
]
# the reader that came from the file keeps its section as the user wrote it, macro and all,
# even though the session has resolved its shape since
assert saved.get("booted", "uri") == "{qed.native}/c16.dat"
assert saved.get("booted", "shape") == "65, 65"
assert saved.get("booted", "cell") == "c16"
# and saving it explicitly changes nothing, since all that is missing is nothing
before = text()
store.persistSource(name="booted")
assert text() == before
# and the other reader of the session is nowhere to be found
assert saved.get("second") is None

# saving it again changes nothing
before = text()
store.persistSource(name="first")
assert text() == before

# a reader that came through an archive: the archive hands out keys, and says how to get in
archive = types.SimpleNamespace(
    credentials=lambda: {"region": "us-west-2", "access_key": "AKIATEST", "secret_key": "sekrit"},
    access=lambda: {"profile": "st", "region": "us-west-2"},
)
# connect it; the product lives in a bucket, and nobody opens it here
remote = qed.readers.nisar.gslc(name="remote", uri="s3://bucket/products/gslc.h5", archive=archive)
store.connectSource(source=remote)
# and save it
store.persistSource(name="remote")
saved = doc()
# its section says how to get at the product, so that it can outlive its archive
assert dict(saved.get("remote", "credentials")) == {"profile": "st", "region": "us-west-2"}
# and the keys are nowhere in the file
assert "AKIATEST" not in text()
assert "sekrit" not in text()
# let go of it, so the rest of the driver is about the local readers
store.disconnectSource(name="remote")
assert doc().get("remote") is None

# a name that matches nothing writes nothing
before = text()
assert store.persistSource(name="nobody") is None
assert text() == before

# disconnect the reader that was never saved; the files never knew about it
store.disconnectSource(name="second")
assert text() == before

# disconnect the one that was saved; its entry and its section go
store.disconnectSource(name="first")
after = doc()
assert after.get("first") is None
assert list(after.get("datasets")) == ["qed.readers.native.flat#booted"]

# disconnect the one that came from the file; its entry goes, and so does its section, since
# it lives in the workspace file
store.disconnectSource(name="booted")
final = doc()
assert final.get("booted") is None
assert list(final.get("datasets")) == []

# clean up
os.chdir(here)
shutil.rmtree(workspace)


# end of file
