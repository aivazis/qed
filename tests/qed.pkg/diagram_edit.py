#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise adding factories to a pipeline diagram and removing them, through the store
"""

# externals
import types
import uuid

# support
import qed


# a store stand-in whose only viewport shows {diagram}
def storeOf(diagram):
    """
    Make a store with one viewport whose view draws {diagram}
    """
    # the view
    view = types.SimpleNamespace(diagram=lambda: diagram)
    # the viewport
    port = types.SimpleNamespace(view=lambda: view)
    # the store
    store = types.SimpleNamespace(_viewports=[port])
    # with the store's own search for factories
    store.implementer = lambda **kwds: qed.ux.store.implementer(store, **kwds)
    # hand it off
    return store


# an empty diagram, under a name of its own
def empty():
    """
    Make an empty diagram; pyre hands back the old instance for a name it has seen before
    """
    # easy enough
    return qed.ux.diagram(name=f"diagram_edit.{uuid.uuid1()}", flow=None)


# the store methods, borrowed from the store class
def add(store, family, position):
    """
    Ask {store} to place a factory of {family} at {position}
    """
    # easy enough
    return qed.ux.store.diagramAdd(store, viewport=0, family=family, position=position)


def remove(store, node):
    """
    Ask {store} to remove {node}
    """
    # easy enough
    return qed.ux.store.diagramRemove(store, viewport=0, node=node.relay)


# the factory of {family} on {diagram}
def factoryOf(diagram, family):
    """
    Find the factory of {family} on {diagram}
    """
    # look for it
    return next(entity for entity in diagram.factories if entity.factory.pyre_family() == family)


# placing factories
def adding():
    """
    Place the rgb colormap on an empty diagram, then try to place another on top of it
    """
    # an empty diagram
    diagram = empty()
    store = storeOf(diagram)
    # place the rgb colormap
    result = add(store, "pyre.viz.colormaps.rgb", (0, 0, 0))
    # the store hands back the diagram
    assert result is diagram
    # which now holds the colormap, with its three inputs and three outputs
    assert len(diagram.factories) == 1
    assert len(diagram.slots) == 6
    # the factory is in the flow of the diagram as well
    rgb = factoryOf(diagram, "pyre.viz.colormaps.rgb")
    assert rgb.factory in diagram.flow.factories
    # another one on top of it does not fit, so it is refused
    add(store, "pyre.viz.colormaps.rgb", (0, 0, 0))
    assert len(diagram.factories) == 1
    # and so is a factory nobody offers
    add(store, "pyre.viz.colormaps.nonsense", (40, 0, 0))
    assert len(diagram.factories) == 1
    # all done
    return


# removing factories
def removing():
    """
    Place the gray colormap and the encoder, bind one slot between them, and remove the encoder
    """
    # an empty diagram
    diagram = empty()
    store = storeOf(diagram)
    # place the colormap and the encoder, apart
    add(store, "pyre.viz.colormaps.gray", (0, 0, 0))
    add(store, "pyre.viz.codecs.bmp", (15, 0, 0))
    gray = factoryOf(diagram, "pyre.viz.colormaps.gray")
    bmp = factoryOf(diagram, "pyre.viz.codecs.bmp")
    # four slots each
    assert len(diagram.slots) == 8
    # bind the red output of the colormap to the red input of the encoder, by dropping the one on
    # the other
    red = next(slot for slot in gray.slots if slot.writers and slot.position[1] < 0)
    target = next(slot for slot in bmp.slots if slot.readers and slot.position[1] < 0)
    qed.ux.store.diagramMove(
        store, viewport=0, node=red.relay, position=target.position, settled=True
    )
    # one slot fewer
    assert len(diagram.slots) == 7
    # remove the encoder
    result = remove(store, bmp)
    # the store hands back the diagram
    assert result is diagram
    # the encoder is gone, from the diagram and from its flow
    assert bmp not in diagram.factories
    assert bmp.factory not in diagram.flow.factories
    # so are its own slots, but the slot it shared with the colormap stays, connected to the
    # colormap only
    assert len(diagram.slots) == 4
    assert red in diagram.slots
    assert set(red.writers) == {gray} and not red.readers
    # and nothing on the diagram mentions the encoder any more
    assert all(label.owner is not bmp for label in diagram.labels)
    assert all(connector.factory is not bmp for connector in diagram.connectors)
    # all done
    return


# the driver
def test():
    """
    Add and remove factories
    """
    # add
    adding()
    # and remove
    removing()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
