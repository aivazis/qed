#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise moving the nodes of a pipeline diagram through the store: factories and slots move on
their own, a factory cannot land on another node, and a slot dropped on another merges with it
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
    # and the store
    return types.SimpleNamespace(_viewports=[port])


# move a node through the store
def move(store, node, position):
    """
    Ask {store} to move {node} to {position}
    """
    # borrow the method of the store class
    return qed.ux.store.diagramMove(store, viewport=0, node=node.relay, position=position)


# the gray colormap on a diagram of its own
def gray():
    """
    Draw the gray colormap at the origin, and hand back the diagram and the factory
    """
    # an empty diagram, under a name of its own: pyre hands back the old instance for a name it
    # has seen before
    diagram = qed.ux.diagram(name=f"diagram_move.{uuid.uuid1()}", flow=None)
    # with the colormap on it
    factory, *_ = diagram.addFactory(factory=qed.viz.colormaps.gray()(), position=(0, 0, 0))
    # hand them off
    return diagram, factory


# the slot of {factory} for the trait {name}
def slotOf(factory, name):
    """
    Find the slot of {factory} that is connected to its trait {name}
    """
    # go through the slots of the factory
    for slot in factory.slots:
        # and their connections
        for connector in slot.connections(factory=factory):
            # look for the trait
            if any(trait.name == name for trait in connector):
                # found it
                return slot
    # not there
    return None


# factories and slots move on their own
def independent():
    """
    Move the factory, then one of its slots
    """
    # draw
    diagram, factory = gray()
    store = storeOf(diagram)
    # remember where the slots are
    before = {slot.eid: slot.position for slot in diagram.slots}
    # move the factory
    result = move(store, factory, (2, 4, 0))
    # the store hands back the diagram
    assert result is diagram
    # the factory moved
    assert factory.position == (2, 4, 0)
    # its label followed, keeping its distance
    (label,) = [label for label in factory.labels if label.category == "factory"]
    assert label.position == (2, 1.5, 0)
    # its slots stayed where they were
    assert {slot.eid: slot.position for slot in diagram.slots} == before
    # the layout knows where the factory is now
    assert diagram.layout[(2, 4, 0)] is factory
    # move the output slot for red
    red = slotOf(factory, "red")
    move(store, red, (9, -6, 0))
    # it moved
    assert red.position == (9, -6, 0)
    # and the label of its connector followed it, to where the connector places it
    (connector,) = list(red.connections(factory=factory))
    assert tuple(connector.traitLabel.position) == tuple(connector.placeLabel())
    # which is next to the slot, in its plane
    assert connector.traitLabel.position[2] == red.position[2]
    # all done
    return


# a factory cannot land on another node
def blocked():
    """
    Try to drop the factory on one of its slots
    """
    # draw
    diagram, factory = gray()
    store = storeOf(diagram)
    # the slot for green
    green = slotOf(factory, "green")
    # try to land the factory on it
    move(store, factory, green.position)
    # the factory stayed home
    assert factory.position == (0, 0, 0)
    # and both are still on the layout
    assert diagram.layout[(0, 0, 0)] is factory
    assert diagram.layout[green.position] is green
    # all done
    return


# a slot dropped on another merges with it
def merge():
    """
    Drop the input slot of the colormap on its output slot for red
    """
    # draw
    diagram, factory = gray()
    store = storeOf(diagram)
    # the two slots
    data = slotOf(factory, "data")
    red = slotOf(factory, "red")
    # drop the input on the output
    move(store, data, red.position)
    # there is one slot fewer
    assert len(diagram.slots) == 3
    # the one that moved survives, and carries both connections
    assert data in diagram.slots and red not in diagram.slots
    assert data.readers and data.writers
    # all done
    return


# a node the diagram does not know is left alone
def stale():
    """
    Ask to move a node that is not on the diagram
    """
    # draw
    diagram, factory = gray()
    store = storeOf(diagram)
    # ask with an id that parses but names nothing here
    result = qed.ux.store.diagramMove(
        store, viewport=0, node="Factory:00000000-0000-0000-0000-000000000000", position=(1, 1, 0)
    )
    # the diagram comes back unchanged
    assert result is diagram
    assert factory.position == (0, 0, 0)
    # and so does one with an id that does not parse
    assert (
        qed.ux.store.diagramMove(store, viewport=0, node="nonsense", position=(1, 1, 0)) is diagram
    )
    # all done
    return


# the driver
def test():
    """
    Move nodes around
    """
    # on their own
    independent()
    # into each other
    blocked()
    merge()
    # and ones that are not there
    stale()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
