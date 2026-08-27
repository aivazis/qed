#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that identical tile requests share one render: both subscribers receive the payload of
a single execution, and the team releases the spool once everybody has been served
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


# a task builder with fixed geometry, so the two requests compare equal
def build():
    """
    Describe the same tile request
    """
    # same spec every time
    return qed.nexus.tile(
        view=view, channel="d16.amplitude", zoom=(0, 0), origin=(0, 0), shape=(64, 64)
    )


# build a team
team = qed.nexus.team(name="qed.test.shared")
# with a single crew member
team.size = 1
# the outcome drop box, keyed by subscriber
outcomes = {}
# and a spot to watch the shared spool
spools = []


# the delivery callback factory
def deliver(label):
    """
    Build a callback that records the payload under {label}
    """

    # the callback
    def callback(result, error):
        """
        Map the shared spool and take a private copy of the payload
        """
        # every render succeeds here
        assert error is None
        # remember the spool, so the release can be checked after delivery
        spools.append(result)
        # map it; the team holds it open until every subscriber has been served
        view = result.view()
        # take a private copy
        outcomes[label] = bytes(view)
        # and release the mapping
        view.close()
        # once both subscribers hear back
        if len(outcomes) == 2:
            # wind down the event loop
            team.dispatcher.stop()
        # all done
        return

    # hand it off
    return callback


# two identical requests from two different subscribers
team.assign(task=build(), callback=deliver(label="first"))
team.assign(task=build(), callback=deliver(label="second"))
# the second joined the first: one task queued, one ledger with two subscribers
assert len(team.workplan) == 1
assert len(team.pending) == 1

# spin until both are served
team.dispatcher.watch()
# send the crews home
team.disband()

# both subscribers were served
assert set(outcomes) == {"first", "second"}
# the payloads came from a single shared render
assert outcomes["first"] == outcomes["second"]
# and match the inline reference
assert outcomes["first"] == reference
# both callbacks saw the same spool
assert len(spools) == 2 and spools[0] is spools[1]
# which the team released after delivery
assert spools[0].file is None


# end of file
