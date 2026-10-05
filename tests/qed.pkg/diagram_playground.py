#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the pipeline diagram that belongs to no view, and the search for a diagram by its id
"""

# externals
import types
import uuid

# support
import qed


# a store stand-in with one view that draws {diagram}
def storeOf(diagram):
    """
    Make a store with no playground yet, and one viewport whose view draws {diagram}
    """
    # the view
    view = types.SimpleNamespace(diagram=lambda: diagram)
    # the viewport
    port = types.SimpleNamespace(view=lambda: view)
    # the store, under a name of its own: pyre hands back the old instance for a name it has
    # seen before
    store = types.SimpleNamespace(
        pyre_name=f"diagram_playground.{uuid.uuid1()}", _playground=None, _viewports=[port]
    )
    # with the store's own playground
    store.playground = lambda: qed.ux.store.playground(store)
    # hand it off
    return store


# the driver
def test():
    """
    Draw the playground, and find it and the diagram of a view by their ids
    """
    # the diagram of the view
    drawn = qed.ux.diagram(name=f"diagram_playground.{uuid.uuid1()}", flow=None)
    # and the store
    store = storeOf(drawn)
    # draw the playground
    playground = store.playground()
    # it starts with a colormap and an encoder
    assert sorted(factory.factory.pyre_family() for factory in playground.factories) == [
        "pyre.viz.codecs.bmp",
        "pyre.viz.colormaps.gray",
    ]
    # and lasts
    assert store.playground() is playground
    # its id finds it
    assert qed.ux.store.findDiagram(store, relay=playground.relay) is playground
    # the id of the view's diagram finds that one
    assert qed.ux.store.findDiagram(store, relay=drawn.relay) is drawn
    # and an id that names no diagram finds nothing
    assert qed.ux.store.findDiagram(store, relay="nonsense") is None
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
