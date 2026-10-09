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


# a store stand-in that knows only {diagram}
def storeOf(diagram):
    """
    Make a store whose only pipeline diagram is {diagram}
    """
    # the store finds the diagram by its id, and remembers the id for the requests
    return types.SimpleNamespace(
        findDiagram=lambda relay: diagram if relay == diagram.relay else None,
        relay=diagram.relay,
    )


# move a node through the store
def move(store, node, position, settled=True):
    """
    Ask {store} to move {node} to {position}; a move that is not {settled} is a step of a drag
    """
    # borrow the method of the store class
    return qed.ux.store.diagramMove(
        store, diagram=store.relay, node=node.relay, position=position, settled=settled
    )


# the gray colormap on a diagram of its own
def gray_():
    """
    Draw the gray colormap at the origin, and hand back the diagram and the factory
    """
    # an empty diagram, under a name of its own: pyre hands back the old instance for a name it
    # has seen before
    diagram = qed.ux.diagram(name=f"diagram_move.{uuid.uuid1()}", recipe=None)
    # with the colormap on it
    factory, *_ = diagram.addFactory(pin=qed.viz.colormaps.gray(), position=(0, 0, 0))
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
    diagram, factory = gray_()
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
    # its slots, which are its own and unbound, came along, keeping their places around it
    assert {slot.eid: slot.position for slot in diagram.slots} == {
        eid: (x + 2, y + 4, z) for eid, (x, y, z) in before.items()
    }
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


# a factory takes its own unbound slots along, but not the ones it shares
def group():
    """
    Bind the red output of the colormap to the red input of the encoder, then move the colormap
    """
    # draw the colormap at the origin
    diagram, gray = gray_()
    store = storeOf(diagram)
    # and the encoder to its right
    bmp, *_ = diagram.addFactory(pin=qed.viz.encoders.bmp(), position=(15, 0, 0))
    # bind the two reds
    red = slotOf(gray, "red")
    move(store, red, slotOf(bmp, "red").position)
    # the colormap's own slots, and where they are
    own = {slot.eid: slot.position for slot in diagram.followers(node=gray)}
    # are the three it does not share
    assert len(own) == 3 and red.eid not in own
    # move the colormap down
    move(store, gray, (0, 10, 0))
    # its own slots came along
    assert {slot.eid: slot.position for slot in diagram.followers(node=gray)} == {
        eid: (x, y + 10, z) for eid, (x, y, z) in own.items()
    }
    # the shared one stayed with the binding
    assert red.position == slotOf(bmp, "red").position
    # all done
    return


# a factory whose own slot would land on another node stays where it is
def crowded():
    """
    Move the colormap so that one of its slots would land on a slot of the encoder
    """
    # draw the colormap at the origin
    diagram, gray = gray_()
    store = storeOf(diagram)
    # and the encoder to its right
    bmp, *_ = diagram.addFactory(pin=qed.viz.encoders.bmp(), position=(15, 0, 0))
    # the output of the colormap for green, and the input of the encoder for green
    green = slotOf(gray, "green")
    target = slotOf(bmp, "green")
    # the move that would put the one on the other
    delta = tuple(t - g for t, g in zip(target.position, green.position))
    # try it
    move(store, gray, delta)
    # the colormap stayed home, and so did its slot
    assert gray.position == (0, 0, 0)
    assert green.position == (5, 0, 0)
    # all done
    return


# a selection moves as one, with the slots its factories take along
def selection():
    """
    Pick the colormap and the encoder, which share a binding, and move them together; then try a
    move that would land one of them on a node outside the selection
    """
    # draw the colormap at the origin
    diagram, gray = gray_()
    store = storeOf(diagram)
    # and the encoder to its right
    bmp, *_ = diagram.addFactory(pin=qed.viz.encoders.bmp(), position=(15, 0, 0))
    # bind the two reds
    red = slotOf(gray, "red")
    move(store, red, slotOf(bmp, "red").position)
    # where everything is
    before = {node.eid: node.position for node in [*diagram.factories, *diagram.slots]}
    # move the two factories down by ten, led by the encoder; the slot they share connects only
    # to them, so it comes along without being picked
    qed.ux.store.diagramMoveGroup(
        store,
        diagram=store.relay,
        nodes=[gray.relay, bmp.relay],
        anchor=bmp.relay,
        position=(15, 10, 0),
    )
    # everything moved by the same amount, the shared slot included
    after = {node.eid: node.position for node in [*diagram.factories, *diagram.slots]}
    assert after == {eid: (x, y + 10, z) for eid, (x, y, z) in before.items()}
    # a lone factory, placed where the group would land if it moved down by ten more
    lone, *_ = diagram.addFactory(pin=qed.viz.normalizers.parametric(), position=(0, 20, 0))
    # where the group is now
    before = after
    # the move that would land the colormap on it
    qed.ux.store.diagramMoveGroup(
        store,
        diagram=store.relay,
        nodes=[gray.relay, bmp.relay],
        anchor=gray.relay,
        position=(0, 20, 0),
    )
    # is refused: nothing in the group moved
    assert {node.eid: node.position for node in [gray, bmp, *gray.slots, *bmp.slots]} == {
        eid: position
        for eid, position in before.items()
        if eid in {node.eid for node in [gray, bmp, *gray.slots, *bmp.slots]}
    }
    # all done
    return


# a factory cannot land on another node
def blocked():
    """
    Try to drop the factory on one of its slots
    """
    # draw
    diagram, factory = gray_()
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
    diagram, factory = gray_()
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


# a drag that reports its steps merges only where it lands
def steps():
    """
    Drag the input slot across the output slot for red, in steps, and drop it on the one for blue
    """
    # draw
    diagram, factory = gray_()
    store = storeOf(diagram)
    # the slots
    data = slotOf(factory, "data")
    red = slotOf(factory, "red")
    blue = slotOf(factory, "blue")
    # a step onto the slot for red
    move(store, data, red.position, settled=False)
    # moves the node there, but merges nothing yet
    assert data.position == red.position
    assert len(diagram.slots) == 4
    # the node is on the move, out of the layout, which still knows the slot for red
    assert diagram.migrant is data
    assert diagram.layout[red.position] is red
    # the drop, onto the slot for blue
    move(store, data, blue.position)
    # merges with the slot for blue only
    assert len(diagram.slots) == 3
    assert blue not in diagram.slots and red in diagram.slots
    # and the drag is over
    assert diagram.migrant is None
    # all done
    return


# a drag that was left in the middle lands where it was last seen
def abandoned():
    """
    Start dragging the factory, and move a slot before the factory is dropped
    """
    # draw
    diagram, factory = gray_()
    store = storeOf(diagram)
    # a step of a drag of the factory that never ends
    move(store, factory, (3, 3, 0), settled=False)
    # the factory is on the move
    assert diagram.migrant is factory
    # move a slot
    red = slotOf(factory, "red")
    move(store, red, (11, 11, 0))
    # the factory landed where it was last seen, and is back on the layout
    assert factory.position == (3, 3, 0)
    assert diagram.layout[(3, 3, 0)] is factory
    # and the slot moved
    assert diagram.layout[(11, 11, 0)] is red
    # nothing is on the move any more
    assert diagram.migrant is None
    # all done
    return


# a node the diagram does not know is left alone
def stale():
    """
    Ask to move a node that is not on the diagram
    """
    # draw
    diagram, factory = gray_()
    store = storeOf(diagram)
    # ask with an id that parses but names nothing here
    result = qed.ux.store.diagramMove(
        store,
        diagram=store.relay,
        node="Factory:00000000-0000-0000-0000-000000000000",
        position=(1, 1, 0),
    )
    # the diagram comes back unchanged
    assert result is diagram
    assert factory.position == (0, 0, 0)
    # and so does one with an id that does not parse
    assert (
        qed.ux.store.diagramMove(store, diagram=store.relay, node="nonsense", position=(1, 1, 0))
        is diagram
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
    # in groups
    group()
    crowded()
    selection()
    # in steps, and left half way
    steps()
    abandoned()
    # and ones that are not there
    stale()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
