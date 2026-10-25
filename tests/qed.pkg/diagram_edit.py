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
    # with the protocols the store offers
    store.palette = lambda: qed.ux.store.palette(store)
    # and its own search for factories
    store.implementer = lambda **kwds: qed.ux.store.implementer(store, **kwds)
    # hand it off
    return store


# an empty diagram, under a name of its own
def empty():
    """
    Make an empty diagram; pyre hands back the old instance for a name it has seen before
    """
    # easy enough
    return qed.ux.diagram(name=f"diagram_edit.{uuid.uuid1()}", recipe=None)


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
    return next(entity for entity in diagram.factories if entity.node.pin.pyre_family() == family)


# placing factories
def adding():
    """
    Place the oklch colormap on an empty diagram, then try to place another on top of it
    """
    # an empty diagram
    diagram = empty()
    # and a store that knows it
    store = storeOf(diagram)
    # place the oklch colormap
    result = add(store, "pyre.viz.colormaps.oklch", (0, 0, 0))
    # the store hands back the diagram
    assert result is diagram
    # which now holds the colormap, with its three inputs and three outputs
    assert len(diagram.factories) == 1
    # and its six slots
    assert len(diagram.slots) == 6
    # the factory is in the recipe of the diagram as well
    oklch = factoryOf(diagram, "pyre.viz.colormaps.oklch")
    # where the recipe finds the node of the factory
    assert diagram.recipe.node(name=oklch.node.name) is oklch.node
    # as a colormap, pinned to the class the palette offers
    assert oklch.node.protocol is qed.viz.colormap
    # pinned to its class
    assert oklch.node.level == "class"
    # another one on top of it does not fit, so it is refused
    add(store, "pyre.viz.colormaps.oklch", (0, 0, 0))
    # so the diagram still holds just the one
    assert len(diagram.factories) == 1
    # and so is a factory nobody offers
    add(store, "pyre.viz.colormaps.nonsense", (40, 0, 0))
    # and the diagram still holds just the one
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
    # and a store that knows it
    store = storeOf(diagram)
    # place the colormap and the encoder, apart
    add(store, "pyre.viz.colormaps.gray", (0, 0, 0))
    # and the encoder to its right
    add(store, "pyre.viz.encoders.bmp", (15, 0, 0))
    # find the colormap
    gray = factoryOf(diagram, "pyre.viz.colormaps.gray")
    # and the encoder
    bmp = factoryOf(diagram, "pyre.viz.encoders.bmp")
    # four slots each
    assert len(diagram.slots) == 8
    # bind the red output of the colormap to the red input of the encoder, by dropping the one on
    # the other
    red = next(slot for slot in gray.slots if slot.writers and slot.position[1] < 0)
    # and the red input of the encoder
    target = next(slot for slot in bmp.slots if slot.readers and slot.position[1] < 0)
    # drop the one on the other, and let it settle
    qed.ux.store.diagramMove(
        store, diagram=store.relay, node=red.relay, position=target.position, settled=True
    )
    # one slot fewer
    assert len(diagram.slots) == 7
    # the slot that stays stands for a new product of the recipe, which both reds are bound to
    product = red.product.name
    # the colormap writes its red into that product
    assert diagram.recipe.binding(factory=gray.node.name, slot="red").product == product
    # and the encoder reads its red from it
    assert diagram.recipe.binding(factory=bmp.node.name, slot="red").product == product
    # and which holds color channels, since that is what both slots expect
    assert red.product.specification is qed.viz.tiles.channel
    # remove the encoder
    result = remove(store, bmp)
    # the store hands back the diagram
    assert result is diagram
    # the encoder is gone, from the diagram and from its recipe
    assert bmp not in diagram.factories
    # and from the recipe
    assert bmp.node.name not in diagram.recipe.nodes
    # so are its own slots, but the slot it shared with the colormap stays, connected to the
    # colormap only
    assert len(diagram.slots) == 4
    # the shared slot is still there
    assert red in diagram.slots
    # written by the colormap, and read by nobody
    assert set(red.writers) == {gray} and not red.readers
    # and still stands for its product, which the colormap writes
    assert [tuple(b) for b in diagram.recipe.bindings] == [(gray.node.name, "red", product)]
    # and nothing on the diagram mentions the encoder any more
    assert all(label.owner is not bmp for label in diagram.labels)
    # nor any of its connectors
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
    # and a store that knows it
    store = storeOf(diagram)
    # the colormap and the encoder
    add(store, "pyre.viz.colormaps.gray", (0, 0, 0))
    # and the encoder to its right
    add(store, "pyre.viz.encoders.bmp", (15, 0, 0))
    # find the colormap
    gray = factoryOf(diagram, "pyre.viz.colormaps.gray")
    # and the encoder
    bmp = factoryOf(diagram, "pyre.viz.encoders.bmp")
    # bind the reds by dropping the output on the input
    red = slotOf(gray, "red")
    # drop it on the red input of the encoder
    move(store, red, slotOf(bmp, "red").position)
    # so the two reds share a slot, one fewer than before
    assert len(diagram.slots) == 7
    # remove the slot of the binding
    remove(store, red)
    # the binding is undone: the slot is gone, and each red has a slot of its own again
    assert red not in diagram.slots
    # so there are eight slots again
    assert len(diagram.slots) == 8
    # each one at its home
    assert slotOf(gray, "red").position == gray.home(trait=gray.node.slots["red"])
    # and so is the red of the encoder
    assert slotOf(bmp, "red").position == bmp.home(trait=bmp.node.slots["red"])
    # connected the way it was, and to nobody else
    assert set(slotOf(gray, "red").writers) == {gray} and not slotOf(gray, "red").readers
    # and the red of the encoder is read by the encoder alone
    assert set(slotOf(bmp, "red").readers) == {bmp} and not slotOf(bmp, "red").writers
    # and the recipe forgot both the bindings and the product
    assert diagram.recipe.bindings == [] and not list(diagram.recipe.products())
    # a slot that is already one trait's own has nothing to undo
    own = slotOf(gray, "green")
    # removing it
    remove(store, own)
    # leaves it on the diagram, with all eight slots
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
    # and a store that knows it
    store = storeOf(diagram)
    # the first filter at the origin, and the second well to its right, for now
    add(store, "pyre.viz.normalizers.parametric", (0, 0, 0))
    # and the second, to its right for now
    add(store, "pyre.viz.normalizers.parametric", (20, 0, 0))
    # tell them apart by where they are
    first, second = sorted(
        (entity for entity in diagram.factories), key=lambda entity: entity.position
    )
    # bind the output of the first to the input of the second, and bring the binding back to
    # the home of the output
    output = slotOf(first, "normalized")
    # drop it on the input of the second, which binds them
    move(store, output, slotOf(second, "signal").position)
    # and bring the binding back to the home of the output
    move(store, output, (5, 0, 0))
    # bring the second filter close, so its input calls the same spot home
    move(store, second, (10, 0, 0))
    # so the home of its input is the spot of the binding
    assert second.home(trait=second.node.slots["signal"]) == (5, 0, 0)
    # split the binding
    remove(store, output)
    # each slot stepped half a cell toward its own factory, so the two do not pile up
    assert slotOf(first, "normalized").position == (4, 0, 0)
    # and the input of the second toward the second
    assert slotOf(second, "signal").position == (6, 0, 0)
    # all done
    return


# slots that expect unrelated specifications cannot be bound
def refusing():
    """
    Drop the magnitudes the amplitude writes on the input of the gray colormap, which expects
    unit values, and check that the binding is refused
    """
    # an empty diagram
    diagram = empty()
    # and a store that knows it
    store = storeOf(diagram)
    # the amplitude, and the colormap well to its right
    add(store, "pyre.viz.operators.amplitude", (0, 0, 0))
    # and the colormap well to its right
    add(store, "pyre.viz.colormaps.gray", (20, 0, 0))
    # find the amplitude
    amplitude = factoryOf(diagram, "pyre.viz.operators.amplitude")
    # and the colormap
    gray = factoryOf(diagram, "pyre.viz.colormaps.gray")
    # the output of the amplitude
    output = slotOf(amplitude, "amplitude")
    # where it is
    origin = output.position
    # dropped on the input of the colormap
    move(store, output, slotOf(gray, "data").position)
    # stays where it was
    assert output.position == origin
    # and binds nothing
    assert diagram.recipe.bindings == []
    # and every slot is still there
    assert len(diagram.slots) == 6
    # all done
    return


# a diagram drawn read only
def readonly():
    """
    Draw the covariance flow read only, and check that adding, removing, binding, and splitting
    leave it as it is, while moving a node still works
    """
    # draw the flow as a recipe pinned to its instances, under a name of its own
    diagram = qed.ux.diagram(
        name=f"diagram_edit.{uuid.uuid1()}",
        recipe=qed.flow.recipe.harvest(flow=qed.channels.covariance()),
        editable=False,
    )
    # and a store that knows it
    store = storeOf(diagram)

    # what it looks like
    def picture():
        """
        The families of the factories, and where every node is
        """
        # collect them
        return (
            sorted(factory.node.pin.pyre_family() for factory in diagram.factories),
            sorted(node.position for node in [*diagram.factories, *diagram.slots]),
        )

    # take a picture of it before any edits
    before = picture()
    # adding a factory
    add(store, "pyre.viz.filters.power", (0, 30, 0))
    # removing one
    remove(store, next(iter(diagram.factories)))
    # and splitting a bound slot
    remove(store, next(slot for slot in diagram.slots if slot.readers and slot.writers))
    # change nothing
    assert picture() == before
    # dropping a slot that is not shared on another one
    loose = [slot for slot in diagram.slots if not (slot.readers and slot.writers)]
    # pick two of them
    first, second = loose[0], loose[1]
    # remember where the first one is
    origin = first.position
    # drop the first on the second, and let it settle
    qed.ux.store.diagramMove(
        store, diagram=store.relay, node=first.relay, position=second.position, settled=True
    )
    # binds nothing: the slot stays where it was
    assert first.position == origin
    # and the picture is unchanged
    assert picture() == before
    # but a move to an empty spot goes through
    qed.ux.store.diagramMove(
        store, diagram=store.relay, node=first.relay, position=(0, 40, 0), settled=True
    )
    # and the slot is where it was sent
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
    # and split them in a packed diagram
    packed()
    # refuse bindings of unrelated specifications
    refusing()
    # a diagram that cannot be edited
    readonly()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
