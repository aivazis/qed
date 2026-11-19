#!/usr/bin/env python3
# -*- python -*-
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
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# get the reader
reader, *_ = ux.store.sources
# and its dataset
dataset, *_ = reader.datasets
# grab the amplitude pipeline
pipeline = dataset.channel(name="amplitude")

# assemble a stand-in for the view state behind a tile request
view = types.SimpleNamespace(reader=reader, dataset=dataset, pipeline=lambda channel: pipeline)


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
# made twice
two = build()
# are equal
assert one == two
# and hash the same
assert hash(one) == hash(two)
# and set/dict machinery treats them as one
assert len({one, two}) == 1

# a different geometry is different work
other = qed.nexus.tile(
    view=view, channel="d16.amplitude", zoom=(0, 0), origin=(8, 8), shape=(64, 64)
)
# so it is not equal
assert one != other

# and so is the same geometry under different controller state
low = pipeline.amplitude.low
# nudge the low end of the amplitude
pipeline.amplitude.low = low + 0.25
# make the request
tweaked = build()
# and put the low end back
pipeline.amplitude.low = low
# so the request is different work
assert one != tweaked

# a fresh harvest after the restore matches the original again
restored = build()
# so it is the same work
assert one == restored

# the display bounds are presentation only, so moving them is the same work
minimum = pipeline.amplitude.min
# widen the display bounds
pipeline.amplitude.min = minimum - 1.0
# make the request
reframed = build()
# and put the bounds back
pipeline.amplitude.min = minimum
# so the request is the same work
assert one == reframed
# and so is pinning the controller, or releasing it
auto = pipeline.amplitude.auto
# flip the flag
pipeline.amplitude.auto = not auto
# make the request
flipped = build()
# and put the flag back
pipeline.amplitude.auto = auto
# so the request is the same work
assert one == flipped


# end of file
