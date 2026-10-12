#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Nothing goes on the ends of a factory, a cell away from it on either side, where its connectors
meet: a node there would look connected to something it is not. A slot moved, alone or with a
group, onto the end of a factory stays where it was; a factory moved so that one of its ends lands
on a node stays where it was; a factory from the palette does not fit with its spot on the end of
another; and the spots found for new slots are never ends
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
def move(store, node, position):
    """
    Ask {store} to move {node} to {position}, and let it land
    """
    # borrow the method of the store class
    return qed.ux.store.diagramMove(
        store, diagram=store.relay, node=node.relay, position=position, settled=True
    )


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


# the driver
def test() -> None:
    """
    Try to put nodes on the ends of the gray colormap, and the ends of the encoder on a node
    """
    # an empty diagram, under a name of its own: pyre hands back the old instance for a name it
    # has seen before
    diagram = qed.ux.diagram(name=f"diagram_ends.{uuid.uuid1()}", recipe=None)
    store = storeOf(diagram)
    # with the gray colormap at the origin, whose ends are a cell away on either side
    gray, *_ = diagram.addFactory(pin=qed.viz.colormaps.gray(), position=(0, 0, 0))
    assert gray.ends() == [(-2, 0, 0), (2, 0, 0)], gray.ends()
    # and the encoder well to its right
    bmp, *_ = diagram.addFactory(pin=qed.viz.encoders.bmp(), position=(30, 0, 0))

    # the slot of the red output of the colormap, and where it is
    red = slotOf(gray, "red")
    home = red.position
    # moved onto either end of the colormap
    for end in gray.ends():
        # it stays where it was
        move(store, red, end)
        assert red.position == home, (end, red.position)
        # and the layout still has it there
        assert diagram.layout[home] is red
    # moved with a group onto an end, it stays too
    assert diagram.moveGroup(nodes=[red], anchor=red, position=(2, 0, 0)) is False
    assert red.position == home

    # the encoder moved so that its input end lands on the slot
    x, y, z = home
    move(store, bmp, (x + 2, y, z))
    # stays where it was
    assert bmp.position == (30, 0, 0), bmp.position
    # while a move that keeps its ends clear goes through
    move(store, bmp, (30, 20, 0))
    assert bmp.position == (30, 20, 0), bmp.position

    # a factory from the palette whose spot is the end of the colormap
    assert not diagram.fits(position=(2, 0, 0), pin=qed.viz.encoders.bmp())
    # does not fit, while one far from everybody does
    assert diagram.fits(position=(2, 60, 0), pin=qed.viz.encoders.bmp())
    # and the spot found for a new slot near an end is never the end itself
    assert diagram.vacancy(spot=(2, 0, 0)) not in gray.ends()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
