#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a setting a person changed interactively gets into the configuration files when the
session is saved, even though it was set at the priority of the command line, while a value that
came from the command line itself stays out; the file brings the edit back at boot with its own
priority, so the next command line overrides it

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "persist_interactive_ws")
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
edited:
    uri: "{qed.native}/c16.dat"
    shape: 65, 65
    cell: c16

# attach it
datasets:
    - qed.readers.native.flat#edited

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
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store
# the reader boot attached
reader = next(source for source in store.sources if source.pyre_name == "edited")
# the priority of the command line
command = pyre.executive.priority.command

# a person changes its offset in the editor, at the priority of the command line
reader.pyre_setTrait(
    alias="offset",
    value="16",
    priority=command(),
    locator=pyre.tracking.interactive(interface="the flow editor"),
)
# while its selections come from the command line itself
reader.pyre_setTrait(
    alias="selections",
    value={"band": "1"},
    priority=command(),
    locator=pyre.tracking.command(arg="--edited.selections=band:1"),
)
# both took
assert reader.offset == 16 and dict(reader.selections) == {"band": "1"}

# save the session
store.persist(archives=False, views=False)
# load the file
saved = pyre.config.newYamlEditor(uri="qed.yaml")
# the edit is in it
assert str(saved.get("edited", "offset")) == "16", saved.get("edited", "offset")
# the value from the command line is not
assert saved.get("edited", "selections") is None, saved.get("edited", "selections")
# and the rest of the section is as the user wrote it
assert saved.get("edited", "uri") == "{qed.native}/c16.dat"
assert saved.get("edited", "shape") == "65, 65"


# end of file
