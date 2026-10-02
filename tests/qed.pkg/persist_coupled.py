#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the controllers the channels of a dataset share are written once, under the name of
their quantity in the namespace of the dataset, and that the channels that share them record
nothing about the binding, which the next session makes again

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "persist_coupled_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it
os.makedirs(workspace)
# with a configuration file that points at the raster in this directory, and leaves the
# controllers to tune themselves
with open(os.path.join(workspace, "qed.yaml"), mode="w", encoding="utf-8") as stream:
    # write it
    stream.write("""# -*- pyre -*-

# the location of the rasters
qed.native: ..

# the dataset
d16:
    uri: "{qed.native}/c16.dat"
    shape: 65, 65
    cell: c16

# connect it
datasets:
    - qed.readers.native.flat#d16

# end of file
""")
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
# make first contact, which tunes the controllers of the reference channels
store.open()
# get the reader
reader, *_ = store.sources
# and its dataset
dataset, *_ = reader.datasets
# the amplitude controller its channels share
amplitude = dataset.channel(name="complex").amplitude

# write everything
store.persist()
# read it back
doc = pyre.config.newYamlEditor(uri="qed.yaml")
# the shared controller has a section under the name of its quantity
assert float(doc.get("d16.data.controllers.amplitude", "low")) == amplitude.low
assert float(doc.get("d16.data.controllers.amplitude", "high")) == amplitude.high
# as do the others the channels share
assert doc.get("d16.data.controllers.phase") is not None
assert doc.get("d16.data.controllers.saturation") is not None
# the channels that share them record nothing about the binding
for channel in ("complex", "amplitude", "phase"):
    # whatever else they may say
    section = doc.get(f"d16.data.{channel}") or {}
    # none of them names a shared controller
    assert not {"amplitude", "phase", "saturation"} & set(section), (channel, dict(section))
# the controllers that belong to a single channel stay under it
assert doc.get("d16.data.real.range") is not None
# and none were written under the names the channels made for themselves at construction
assert doc.get("d16.data.complex.amplitude") is None
assert doc.get("d16.data.amplitude.amplitude") is None

# a second write is idempotent
store.persist()
again = pyre.config.newYamlEditor(uri="qed.yaml")
assert again.render() == doc.render()


# end of file
