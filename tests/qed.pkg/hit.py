#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a render delivered through the fleet lands in the cache, and that an identical
later request is a hit with the exact payload
"""

# externals
import types

# support
import pyre
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
# render the reference tile inline
reference = bytes(
    memoryview(
        dataset.render(channel=pipeline, zoom=(0, 0), origin=(0, 0), shape=(64, 64))
    )
)

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


# build a fleet
fleet = qed.nexus.fleet(name="qed.test.hit")
# give it an event loop
fleet.dispatcher = pyre.ipc.newPSL()
# the outcome drop box
outcomes = []


# the delivery callback
def deliver(result, error):
    """
    Record the outcome and stop the event loop
    """
    # the render succeeds
    assert error is None
    # take note; the payload stays with the cache
    outcomes.append(result)
    # and wind down
    fleet.dispatcher.stop()
    # all done
    return


# nothing is cached before the first render
assert fleet.lookup(task=build()) is None

# render through the fleet
fleet.render(task=build(), callback=deliver)
# spin until delivered
fleet.dispatcher.watch()
# the render arrived
assert len(outcomes) == 1

# an identical later request is a hit
cached = fleet.lookup(task=build())
assert cached is not None
# still open, since the cache owns it
assert cached.file is not None
# and pixel-identical to the inline reference
mapped = cached.view()
assert bytes(mapped) == reference
mapped.close()

# a different request is a miss
assert (
    fleet.lookup(
        task=qed.nexus.tile(
            view=view,
            channel="d16.amplitude",
            zoom=(0, 0),
            origin=(8, 8),
            shape=(64, 64),
        )
    )
    is None
)

# disband the fleet, which releases the cache
fleet.disband()
assert cached.file is None


# end of file
