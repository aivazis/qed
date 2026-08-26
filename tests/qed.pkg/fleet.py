#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a fleet routes tiles to per-product teams and respects its crew budget
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
# get the configured reader
one, *_ = ux.store.sources
# and open the same raster a second time as an independent data product
two = qed.readers.native.flat(name="d16b", uri="./c16.dat", shape=(65, 65), cell="c16")


# build a task for a {reader}, along with the reference tile it should produce
def prepare(reader):
    """
    Build a tile task against {reader} and render its reference inline
    """
    # get the dataset
    dataset, *_ = reader.datasets
    # and its amplitude pipeline
    pipeline = dataset.channel(name="amplitude")
    # render the reference tile
    reference = bytes(
        memoryview(
            dataset.render(channel=pipeline, zoom=(0, 0), origin=(0, 0), shape=(64, 64))
        )
    )
    # assemble a stand-in for the view state
    view = types.SimpleNamespace(
        reader=reader, dataset=dataset, pipeline=lambda channel: pipeline
    )
    # describe the tile as a task
    task = qed.nexus.tile(
        view=view, channel="d16.amplitude", zoom=(0, 0), origin=(0, 0), shape=(64, 64)
    )
    # and hand both off
    return task, reference


# build the tasks
tasks = {reader.pyre_name: prepare(reader=reader) for reader in (one, two)}

# build a fleet
fleet = qed.nexus.fleet(name="qed.test.fleet")
# give it an event loop
fleet.dispatcher = pyre.ipc.newPSL()
# the outcome drop box
outcomes = {}


# the delivery callback factory
def deliver(key):
    """
    Build a callback that records the outcome for {key} and stops the loop when all are in
    """

    # the callback
    def callback(result, error):
        """
        Record the outcome
        """
        # a successful render arrives parked in a spool the team still holds open; map it
        # now, since the team releases the spool once every subscriber has been served
        payload = None
        if result is not None:
            # take a private copy of the payload
            view = result.view()
            payload = bytes(view)
            # and release the mapping
            view.close()
        # file the report
        outcomes[key] = (payload, error)
        # if everybody has reported
        if len(outcomes) == len(tasks):
            # wind down the event loop
            fleet.dispatcher.stop()
        # all done
        return

    # hand it off
    return callback


# queue the tasks
for name, (task, _) in tasks.items():
    # each with its own callback
    fleet.render(task=task, callback=deliver(key=name))

# each product got its own team; the fleet grows with the loaded data products
assert set(fleet.teams) == set(tasks)

# spin the event loop until all the tiles are delivered
fleet.dispatcher.watch()

# go through the outcomes
for name, (task, reference) in tasks.items():
    # unpack
    result, error = outcomes[name]
    # every render succeeded
    assert error is None
    # and matches its inline reference
    assert result == reference

# send everybody home
fleet.disband()
# which empties the registry
assert fleet.teams == {}


# end of file
