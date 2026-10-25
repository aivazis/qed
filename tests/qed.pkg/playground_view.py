#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise how every client looks at the playground: its projection, the trays of its panel that
are open, and where the cameras look, read and changed through the schema
"""

# externals
import types

# support
import journal
import qed


# a store stand-in that keeps how the playground is looked at, the way a fresh store does
def storeOf():
    """
    Make a store whose playground is flat, unturned, seen from above, with only the inspector
    open
    """
    # the store, with the state of a fresh one
    store = types.SimpleNamespace(
        _playgroundProjection={"kind": "flat", "azimuth": 0, "below": False},
        _playgroundTrays={"inspector"},
        _playgroundCamera=None,
    )
    # how the playground is looked at
    store.playgroundView = lambda: qed.ux.store.playgroundView(store)
    # changing its projection
    store.playgroundProjectionSet = lambda **kwds: qed.ux.store.playgroundProjectionSet(
        store, **kwds
    )
    # pointing the cameras
    store.playgroundCameraSet = lambda **kwds: qed.ux.store.playgroundCameraSet(store, **kwds)
    # and opening or closing a tray
    store.playgroundTraySet = lambda **kwds: qed.ux.store.playgroundTraySet(store, **kwds)
    # hand it off
    return store


# the query
reading = """
    query {
        qed {
            playgroundView { id kind azimuth below trays camera { x y z } }
        }
    }
"""
# the change of projection
projecting = """
    mutation ($payload: PlaygroundProjectionSetInput!) {
        playgroundProjectionSet(input: $payload) {
            view { id kind azimuth below trays camera { x y z } }
        }
    }
"""
# the move of the cameras
pointing = """
    mutation ($payload: PlaygroundCameraSetInput!) {
        playgroundCameraSet(input: $payload) {
            view { id kind azimuth below trays camera { x y z } }
        }
    }
"""
# the change of a tray
toggling = """
    mutation ($payload: PlaygroundTraySetInput!) {
        playgroundTraySet(input: $payload) {
            view { id kind azimuth below trays camera { x y z } }
        }
    }
"""


# the driver
def test():
    """
    Read the view of a fresh playground, turn it isometric and around, open and close trays, point
    the cameras and forget where they looked when the projection changes, and check that a
    projection it does not know leaves the view as it is
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

    # a fresh playground is flat, unturned, seen from above, with only the inspector open
    assert run(reading)["qed"]["playgroundView"] == {
        "id": "playground.view",
        "kind": "flat",
        "azimuth": 0,
        "below": False,
        "trays": ["inspector"],
        "camera": None,
    }
    # turn it isometric, five quarter turns to the left, seen from below
    payload = {"kind": "iso", "azimuth": -5, "below": True}
    # the turns fold into a full turn
    view = run(projecting, {"payload": payload})["playgroundProjectionSet"]["view"]
    # so the view is isometric, three quarter turns around, seen from below
    assert (view["kind"], view["azimuth"], view["below"]) == ("iso", 3, True)
    # and the next reader sees the same
    assert run(reading)["qed"]["playgroundView"] == view
    # open two trays
    for tray in ("readers", "pyre.viz.colormaps"):
        # one at a time
        run(toggling, {"payload": {"tray": tray, "expanded": True}})
    # close one of them, the inspector, and one that is already closed
    for tray in ("readers", "inspector", "designs"):
        # one at a time
        run(toggling, {"payload": {"tray": tray, "expanded": False}})
    # the one left open is the only one
    assert run(reading)["qed"]["playgroundView"]["trays"] == ["pyre.viz.colormaps"]

    # point the cameras
    payload = {"x": 12.5, "y": -3.0, "z": 0.75}
    # and every reader sees where they look
    view = run(pointing, {"payload": payload})["playgroundCameraSet"]["view"]
    # the mutation hands back the camera
    assert view["camera"] == payload
    # and so does a fresh read
    assert run(reading)["qed"]["playgroundView"]["camera"] == payload
    # a change of projection forgets it, since the point belongs to the old projection
    payload = {"kind": "flat", "azimuth": 0, "below": False}
    # switch back to the flat projection
    view = run(projecting, {"payload": payload})["playgroundProjectionSet"]["view"]
    # and the camera is gone
    assert view["camera"] is None
    # put the projection back where the rest of the test expects it
    payload = {"kind": "iso", "azimuth": 3, "below": True}
    # and ask for it
    run(projecting, {"payload": payload})

    # a projection it does not know is reported, so quiet the report
    journal.warning("qed.ux.playground").deactivate()
    # and asked for
    payload = {"kind": "oblique", "azimuth": 1, "below": False}
    # leaves the view as it was
    view = run(projecting, {"payload": payload})["playgroundProjectionSet"]["view"]
    # still isometric, three quarter turns around, seen from below
    assert (view["kind"], view["azimuth"], view["below"]) == ("iso", 3, True)
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
