#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
The contents a flat reader and a picker share on a diagram are a specification while either is a
class, stay one when the picker becomes an instance, and become the reader's own contents once
the reader does, so asking the picker for the selections it can make opens the file
"""

# externals
import os
import types
import uuid

# support
import qed

# the descriptions, as the graphql schema serves them
from qed.gql.diagram.FlowProduct import FlowProduct
from qed.gql.diagram.FlowSlot import FlowSlot

# the cells of this directory: 65 x 65 of them, complex, in double precision
raster = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c16.dat")


# a store stand-in with an empty playground
def storeOf() -> types.SimpleNamespace:
    """
    Make a store with no playground yet and no views
    """
    # the store, under a name of its own: pyre hands back the old instance for a name it has
    # seen before
    store = types.SimpleNamespace(
        pyre_name=f"diagram_realize.{uuid.uuid1()}", _playground=None, _viewports=[]
    )
    # with the store's own playground
    store.playground = lambda: qed.ux.store.playground(store)
    # the search for a diagram by its id
    store.findDiagram = lambda relay: qed.ux.store.findDiagram(store, relay=relay)
    # the protocols on offer
    store.palette = lambda: qed.ux.store.palette(store)
    # the search for what a family names
    store.implementer = lambda family: qed.ux.store.implementer(store, family=family)
    # the drop of a factory from the palette
    store.diagramAdd = lambda **kwds: qed.ux.store.diagramAdd(store, **kwds)
    # the move of a node
    store.diagramMove = lambda **kwds: qed.ux.store.diagramMove(store, **kwds)
    # the pin to a new instance
    store.diagramInstantiate = lambda **kwds: qed.ux.store.diagramInstantiate(store, **kwds)
    # which makes it through the store's helper
    store._instantiate = lambda **kwds: qed.ux.store._instantiate(store, **kwds)
    # hand it off
    return store


# find a slot
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


# what the schema says about a slot
def describe(slot) -> dict:
    """
    Describe {slot} the way the canvas and the inspector see it
    """
    # ask the resolvers
    return {
        "level": FlowSlot.resolve_level(slot, None),
        "empty": FlowSlot.resolve_empty(slot, None),
        "stale": FlowSlot.resolve_stale(slot, None),
        "specification": FlowProduct.resolve_specification(slot, None),
        "family": FlowProduct.resolve_family(slot, None),
        "facts": [(f.name, f.value) for f in FlowProduct.resolve_facts(slot, None)],
    }


# the driver
def test() -> None:
    """
    Wire a flat reader to a picker through their contents, and make them instances
    """
    # make a store
    store = storeOf()
    # its playground
    playground = store.playground()
    # with a flat reader
    store.diagramAdd(diagram=playground.relay, family="qed.readers.native.flat", position=(0, 0, 0))
    (reader,) = playground.factories
    # and a picker
    store.diagramAdd(diagram=playground.relay, family="pyre.viz.pickers.match", position=(8, 0, 0))
    (picker,) = [entity for entity in playground.factories if entity is not reader]

    # drop the contents the reader writes on the ones the picker reads
    store.diagramMove(
        diagram=playground.relay,
        node=slotOf(reader, "contents").relay,
        position=slotOf(picker, "contents").position,
    )
    # the two share a slot
    shared = slotOf(reader, "contents")
    assert shared is slotOf(picker, "contents")
    # which stands for a product that is only a specification
    assert shared.product is not None and shared.product.level == "protocol"
    # and is described as one
    assert describe(shared) == {
        "level": "protocol",
        "empty": False,
        "stale": None,
        "specification": "pyre.viz.contents",
        "family": None,
        "facts": [],
    }, describe(shared)

    # the picker becomes an instance
    _, error = store.diagramInstantiate(
        diagram=playground.relay, node=picker.relay, name=f"realize_{uuid.uuid1().hex[:8]}"
    )
    assert error is None, error
    # which reads the contents, so they stay a specification, and it holds nothing
    assert shared.product.level == "protocol"
    assert picker.node.pin.contents is None
    # while the dataset it writes, which is bound to nothing, is a product of its own, not made yet
    dataset = describe(slotOf(picker, "dataset"))
    assert (dataset["level"], dataset["stale"]) == ("instance", True), dataset
    assert dataset["family"] == "pyre.viz.datasets.memory", dataset
    # so it has no selections to suggest; the diagram cannot change a map until it has an editor
    # for one, so the picker is asked directly
    selection = picker.node.pin.pyre_trait(alias="selection")
    assert list(picker.node.pin.pyre_suggest(trait=selection)) == []

    # the reader becomes an instance that knows its file and its cell
    flat = qed.readers.native.flat(
        name=f"realize_{uuid.uuid1().hex[:8]}", uri=raster, cell="c16", shape=(65, 65)
    )
    playground.pin(entity=reader, pin=flat)
    # so the contents become its own
    assert shared.product.level == "instance"
    assert shared.product.pin is flat.contents
    # which the picker reads
    assert picker.node.pin.contents is flat.contents
    # without opening the file yet
    assert flat.contents.pyre_stale and flat.datasets == []

    # asking the picker for its selections
    selections = list(picker.node.pin.pyre_suggest(trait=selection))
    # pulls the contents, which opens the file and finds its one dataset, on no axes
    assert selections == [{}], selections
    assert len(flat.datasets) == 1
    assert not flat.contents.pyre_stale
    # so the contents are made, and say they hold one dataset, on no axes
    made = describe(shared)
    assert (made["level"], made["stale"]) == ("instance", False), made
    assert made["family"] == "pyre.viz.contents.memory", made
    assert made["facts"] == [("dataset", "")], made

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
