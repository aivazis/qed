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


# a store stand-in that knows only {diagram}
def storeOf(diagram):
    """
    Make a store whose only pipeline diagram is {diagram}
    """
    # the store finds the diagram by its id, and remembers the id for the requests
    store = types.SimpleNamespace(
        findDiagram=lambda relay: diagram if relay == diagram.relay else None,
        relay=diagram.relay,
    )
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
    return qed.ux.store.diagramAdd(store, diagram=store.relay, family=family, position=position)


def remove(store, node):
    """
    Ask {store} to remove {node}
    """
    # easy enough
    return qed.ux.store.diagramRemove(store, diagram=store.relay, node=node.relay)


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
        store, diagram=store.relay, node=red.relay, position=target.position, settled=True
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


# the slot of {factory} for its trait {name}
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


# move a node through the store
def move(store, node, position):
    """
    Ask {store} to move {node} to {position}
    """
    # easy enough
    return qed.ux.store.diagramMove(store, diagram=store.relay, node=node.relay, position=position)


# removing a slot undoes the binding it stands for
def splitting():
    """
    Bind the red output of the colormap to the red input of the encoder, then remove the slot
    """
    # an empty diagram
    diagram = empty()
    store = storeOf(diagram)
    # the colormap and the encoder
    add(store, "pyre.viz.colormaps.gray", (0, 0, 0))
    add(store, "pyre.viz.codecs.bmp", (15, 0, 0))
    gray = factoryOf(diagram, "pyre.viz.colormaps.gray")
    bmp = factoryOf(diagram, "pyre.viz.codecs.bmp")
    # bind the reds by dropping the output on the input
    red = slotOf(gray, "red")
    move(store, red, slotOf(bmp, "red").position)
    assert len(diagram.slots) == 7
    # remove the slot of the binding
    remove(store, red)
    # the binding is undone: the slot is gone, and each red has a slot of its own again
    assert red not in diagram.slots
    assert len(diagram.slots) == 8
    # each one at its home
    assert slotOf(gray, "red").position == gray.home(trait=gray.factory.pyre_trait("red"))
    assert slotOf(bmp, "red").position == bmp.home(trait=bmp.factory.pyre_trait("red"))
    # connected the way it was, and to nobody else
    assert set(slotOf(gray, "red").writers) == {gray} and not slotOf(gray, "red").readers
    assert set(slotOf(bmp, "red").readers) == {bmp} and not slotOf(bmp, "red").writers
    # a slot that is already one trait's own has nothing to undo
    own = slotOf(gray, "green")
    remove(store, own)
    assert own in diagram.slots and len(diagram.slots) == 8
    # all done
    return


# a binding in a packed diagram comes apart along its own line
def packed():
    """
    Two filters ten units apart, so the output of one and the input of the other share a home,
    bound right there, then split
    """
    # an empty diagram
    diagram = empty()
    store = storeOf(diagram)
    # the first filter at the origin, and the second well to its right, for now
    add(store, "pyre.viz.filters.parametric", (0, 0, 0))
    add(store, "pyre.viz.filters.parametric", (20, 0, 0))
    first, second = sorted(
        (entity for entity in diagram.factories), key=lambda entity: entity.position
    )
    # bind the output of the first to the input of the second, and bring the binding back to
    # the home of the output
    output = slotOf(first, "parametric")
    move(store, output, slotOf(second, "signal").position)
    move(store, output, (5, 0, 0))
    # bring the second filter close, so its input calls the same spot home
    move(store, second, (10, 0, 0))
    assert second.home(trait=second.factory.pyre_trait("signal")) == (5, 0, 0)
    # split the binding
    remove(store, output)
    # each slot stepped half a cell toward its own factory, so the two do not pile up
    assert slotOf(first, "parametric").position == (4, 0, 0)
    assert slotOf(second, "signal").position == (6, 0, 0)
    # all done
    return


# a diagram drawn read only
def readonly():
    """
    Draw the covariance flow read only, and check that adding, removing, binding, and splitting
    leave it as it is, while moving a node still works
    """
    # draw the flow, under a name of its own
    diagram = qed.ux.diagram(
        name=f"diagram_edit.{uuid.uuid1()}", flow=qed.channels.covariance(), editable=False
    )
    store = storeOf(diagram)

    # what it looks like
    def picture():
        """
        The families of the factories, and where every node is
        """
        # collect them
        return (
            sorted(factory.factory.pyre_family() for factory in diagram.factories),
            sorted(node.position for node in [*diagram.factories, *diagram.slots]),
        )

    before = picture()
    # adding a factory
    add(store, "pyre.viz.filters.power", (0, 30, 0))
    # removing one
    remove(store, next(iter(diagram.factories)))
    # and splitting a bound slot
    remove(store, next(slot for slot in diagram.slots if slot.readers and slot.writers))
    # change nothing
    assert picture() == before
    # dropping an unbound slot on another one
    loose = [slot for slot in diagram.slots if not (slot.readers and slot.writers)]
    first, second = loose[0], loose[1]
    origin = first.position
    qed.ux.store.diagramMove(
        store, diagram=store.relay, node=first.relay, position=second.position, settled=True
    )
    # binds nothing: the slot stays where it was
    assert first.position == origin
    assert picture() == before
    # but a move to an empty spot goes through
    qed.ux.store.diagramMove(
        store, diagram=store.relay, node=first.relay, position=(0, 40, 0), settled=True
    )
    assert first.position == (0, 40, 0)
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
    # undo bindings
    splitting()
    packed()
    # a diagram that cannot be edited
    readonly()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
