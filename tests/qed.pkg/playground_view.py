#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise how every client looks at the playground: its projection and the trays of its panel
that are open, read and changed through the schema
"""

# externals
import types

# support
import journal
import qed


# a store stand-in that keeps how the playground is looked at, the way a fresh store does
def storeOf():
    """
    Make a store whose playground is flat, unturned, seen from above, with only the tray of the
    picked factory open
    """
    # the store, with the state of a fresh one
    store = types.SimpleNamespace(
        _playgroundProjection={"kind": "flat", "azimuth": 0, "below": False},
        _playgroundTrays={"picked"},
    )
    # how the playground is looked at
    store.playgroundView = lambda: qed.ux.store.playgroundView(store)
    # changing its projection
    store.playgroundProjectionSet = lambda **kwds: qed.ux.store.playgroundProjectionSet(
        store, **kwds
    )
    # and opening or closing a tray
    store.playgroundTraySet = lambda **kwds: qed.ux.store.playgroundTraySet(store, **kwds)
    # hand it off
    return store


# the query
reading = """
    query {
        qed {
            playgroundView { id kind azimuth below trays }
        }
    }
"""
# the change of projection
projecting = """
    mutation ($payload: PlaygroundProjectionSetInput!) {
        playgroundProjectionSet(input: $payload) {
            view { id kind azimuth below trays }
        }
    }
"""
# the change of a tray
toggling = """
    mutation ($payload: PlaygroundTraySetInput!) {
        playgroundTraySet(input: $payload) {
            view { id kind azimuth below trays }
        }
    }
"""


# the driver
def test():
    """
    Read the view of a fresh playground, turn it isometric and around, open and close trays, and
    check that a projection it does not know leaves it as it is
    """
    # make a store
    store = storeOf()
    # the execution context
    context = {"store": store}

    # run a document against the schema
    def run(document, variables=None):
        """
        Execute {document} and hand back its data
        """
        # execute
        result = qed.gql.schema.execute(document, context=context, variables=variables)
        # there must be no errors
        assert not result.errors, result.errors
        # hand back the data
        return result.data

    # a fresh playground is flat, unturned, seen from above, with only the picked tray open
    assert run(reading)["qed"]["playgroundView"] == {
        "id": "playground.view",
        "kind": "flat",
        "azimuth": 0,
        "below": False,
        "trays": ["picked"],
    }
    # turn it isometric, five quarter turns to the left, seen from below
    payload = {"kind": "iso", "azimuth": -5, "below": True}
    # the turns fold into a full turn
    view = run(projecting, {"payload": payload})["playgroundProjectionSet"]["view"]
    assert (view["kind"], view["azimuth"], view["below"]) == ("iso", 3, True)
    # and the next reader sees the same
    assert run(reading)["qed"]["playgroundView"] == view
    # open two trays
    for tray in ("readers", "pyre.viz.colormaps"):
        # one at a time
        run(toggling, {"payload": {"tray": tray, "expanded": True}})
    # close one of them, the picked one, and one that is already closed
    for tray in ("readers", "picked", "designs"):
        # one at a time
        run(toggling, {"payload": {"tray": tray, "expanded": False}})
    # the one left open is the only one
    assert run(reading)["qed"]["playgroundView"]["trays"] == ["pyre.viz.colormaps"]

    # a projection it does not know is reported, so quiet the report
    journal.warning("qed.ux.playground").deactivate()
    # and asked for
    payload = {"kind": "oblique", "azimuth": 1, "below": False}
    # leaves the view as it was
    view = run(projecting, {"payload": payload})["playgroundProjectionSet"]["view"]
    assert (view["kind"], view["azimuth"], view["below"]) == ("iso", 3, True)
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
