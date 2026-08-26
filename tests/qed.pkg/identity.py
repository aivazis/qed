#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that tile tasks carry their full specification as their identity, so identical requests
can share a single execution and differing ones cannot
"""

# externals
import types

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the reader
reader, *_ = ux.store.sources
# and its dataset
dataset, *_ = reader.datasets
# grab the amplitude pipeline
pipeline = dataset.channel(name="amplitude")

# assemble a stand-in for the view state behind a tile request
view = types.SimpleNamespace(
    reader=reader, dataset=dataset, pipeline=lambda channel: pipeline
)


# a task builder with fixed geometry
def build():
    """
    Describe the same tile request
    """
    # same spec every time
    return qed.nexus.tile(
        view=view, channel="d16.amplitude", zoom=(0, 0), origin=(0, 0), shape=(64, 64)
    )


# two identical requests are the same work
one = build()
two = build()
assert one == two
assert hash(one) == hash(two)
# and set/dict machinery treats them as one
assert len({one, two}) == 1

# a different geometry is different work
other = qed.nexus.tile(
    view=view, channel="d16.amplitude", zoom=(0, 0), origin=(8, 8), shape=(64, 64)
)
assert one != other

# and so is the same geometry under different controller state
low = pipeline.amplitude.low
pipeline.amplitude.low = low + 0.25
tweaked = build()
pipeline.amplitude.low = low
assert one != tweaked

# a fresh harvest after the restore matches the original again
restored = build()
assert one == restored


# end of file
