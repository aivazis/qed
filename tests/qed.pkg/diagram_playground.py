#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the pipeline diagram that belongs to no view, which draws the amplitude recipe, and the
search for a diagram by its id
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
    # and the recipe it draws
    store.amplitude = lambda: qed.ux.store.amplitude(store)
    # hand it off
    return store


# the driver
def test():
    """
    Draw the playground, check that it draws the amplitude recipe, and find it and the diagram
    of a view by their ids
    """
    # the diagram of the view
    drawn = qed.ux.diagram(name=f"diagram_playground.{uuid.uuid1()}", recipe=None)
    # and the store
    store = storeOf(drawn)
    # draw the playground
    playground = store.playground()
    # its factories, left to right in the order the data flows through them
    factories = sorted(playground.factories, key=lambda factory: factory.position)
    # are the steps of the amplitude recipe, each one as far down as it is pinned
    assert [(factory.kind(), factory.node.level) for factory in factories] == [
        ("amplitude", "class"),
        ("normalizer", "protocol"),
        ("gray", "class"),
        ("encoder", "protocol"),
    ]
    # every product has a slot of its own, which stands for it
    assert sorted(slot.product.name for slot in playground.slots) == [
        "blue",
        "green",
        "image",
        "magnitude",
        "normalized",
        "red",
        "signal",
    ]
    # and is labeled by its name and the most refined of what its slots expect of it
    assert {label.text[0] for label in playground.labels if label.category == "product"} == {
        "signal:complex",
        "magnitude:magnitude",
        "normalized:unit",
        "red:channel",
        "green:channel",
        "blue:channel",
        "image:raster",
    }
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
