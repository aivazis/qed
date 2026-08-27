#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that tile tasks survive a wire round trip and render faithfully
"""

# externals
import pickle
import types

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# get the reader
reader, *_ = ux.store.sources
# and its dataset
dataset, *_ = reader.datasets
# grab the amplitude pipeline
pipeline = dataset.channel(name="amplitude")
# and record its configured range
low = pipeline.amplitude.low

# adjust the range, standing in for a user manipulating a controller
pipeline.amplitude.low = low + 0.05
# render the reference tile with the adjusted pipeline
reference = bytes(
    memoryview(
        dataset.render(channel=pipeline, zoom=(0, 0), origin=(0, 0), shape=(64, 64))
    )
)

# assemble a stand-in for the view state behind a tile request
view = types.SimpleNamespace(
    reader=reader, dataset=dataset, pipeline=lambda channel: pipeline
)
# describe the tile as a task
task = qed.nexus.tile(
    view=view, channel="d16.amplitude", zoom=(0, 0), origin=(0, 0), shape=(64, 64)
)
# push it through the wire, the way the team marshals it to a crew member
task = pickle.loads(pickle.dumps(task))
# execute it the way a worker does: with a fresh reader registry, so the data source is
# rebuilt from the recipe the task carries
spool = task.execute(readers={})
# the render is parked in a spool of the right size
assert spool.size == len(reference)
# read the payload back
spool.file.seek(0)
tile = spool.file.read()
# and release the spool
spool.close()
# check that the worker render matches the reference
assert tile == reference

# restore the range
pipeline.amplitude.low = low
# render the unadjusted tile
unadjusted = bytes(
    memoryview(
        dataset.render(channel=pipeline, zoom=(0, 0), origin=(0, 0), shape=(64, 64))
    )
)
# and check that the adjustment was actually visible, so the comparison above has teeth
assert tile != unadjusted


# end of file
