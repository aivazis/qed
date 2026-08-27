#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a team of crew processes renders tiles and delivers them to the callback
"""

# externals
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
# describe the tile as a task
task = qed.nexus.tile(
    view=view, channel="d16.amplitude", zoom=(0, 0), origin=(0, 0), shape=(64, 64)
)

# build a team
team = qed.nexus.team(name="qed.test.tiles")
# with a couple of crew members
team.size = 2
# the outcome drop box
outcome = {}


# the delivery callback
def deliver(result, error):
    """
    Record the outcome of the task and stop the event loop
    """
    # a successful render arrives parked in a spool the team still holds open; map it now,
    # since the team releases the spool as soon as every subscriber has been served
    if result is not None:
        # take a private copy of the payload
        view = result.view()
        outcome["payload"] = bytes(view)
        # and release the mapping
        view.close()
    # record the verdict
    outcome["error"] = error
    # and wind down the event loop
    team.dispatcher.stop()
    # all done
    return


# queue the task
team.assign(task=task, callback=deliver)
# spin the event loop until the callback fires
team.dispatcher.watch()
# send the crews home
team.disband()

# check that the render succeeded
assert outcome["error"] is None
# and that the crew render matches the inline reference
assert outcome["payload"] == reference


# end of file
