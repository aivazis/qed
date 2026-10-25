#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the pipeline diagram that belongs to no view: it starts out empty, takes a protocol
dropped from the palette, and is found, along with the diagram of a view, by its id
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
    # the search for a diagram by its id
    store.findDiagram = lambda relay: qed.ux.store.findDiagram(store, relay=relay)
    # the protocols on offer
    store.palette = lambda: qed.ux.store.palette(store)
    # the search for what a family names
    store.implementer = lambda family: qed.ux.store.implementer(store, family=family)
    # and the drop of a factory from the palette
    store.diagramAdd = lambda **kwds: qed.ux.store.diagramAdd(store, **kwds)
    # hand it off
    return store


# the driver
def test():
    """
    Draw the playground, check that it is empty, drop the reader protocol on it, and find it and
    the diagram of a view by their ids
    """
    # the diagram of the view
    drawn = qed.ux.diagram(name=f"diagram_playground.{uuid.uuid1()}", recipe=None)
    # and the store
    store = storeOf(drawn)
    # draw the playground
    playground = store.playground()
    # which has nothing on it
    assert not playground.factories
    # and no slots
    assert not playground.slots
    # and can be edited
    assert playground.editable
    # and lasts
    assert store.playground() is playground

    # drop the reader protocol on it
    store.diagramAdd(
        diagram=playground.relay, family=qed.viz.reader.pyre_family(), position=(0, 0, 0)
    )
    # which lands as one factory pinned to nothing
    assert [
        (factory.role(), factory.family(), factory.node.level) for factory in playground.factories
    ] == [("reader", None, "protocol")]
    # with a slot for the raster it exposes, and nothing else
    assert len(playground.slots) == 1
    # a family that names nothing on offer
    store.diagramAdd(diagram=playground.relay, family="nonsense", position=(20, 0, 0))
    # leaves the playground as it is
    assert len(playground.factories) == 1

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
