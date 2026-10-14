#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
A picker on a diagram, bound to the contents of a NISAR reader: making its dataset before its
selection names every axis is refused, and the refusal reaches the diagram as the product and the
reason, kept apart; the selections it suggests read the way the trait reads a map, and taking
one makes the dataset; a secret map is never edited from the diagram
"""

# externals
import os
import types
import uuid

# support
import qed

# a GSLC product
gslc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "nisar", "gslc.h5")


# a store stand-in with an empty playground
def storeOf() -> types.SimpleNamespace:
    """
    Make a store with no playground yet and no views
    """
    # the store, under a name of its own: pyre hands back the old instance for a name it has
    # seen before
    store = types.SimpleNamespace(
        pyre_name=f"diagram_selection.{uuid.uuid1()}", _playground=None, _viewports=[]
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
    # the change of a setting
    store.diagramConfigure = lambda **kwds: qed.ux.store.diagramConfigure(store, **kwds)
    # which assigns the value through the store's helper
    store._configure = lambda **kwds: qed.ux.store._configure(store, **kwds)
    # and reads maps through another
    store._mapping = lambda **kwds: qed.ux.store._mapping(store, **kwds)
    # with the priorities of the executive
    store.pyre_executive = qed.ux.store.pyre_executive
    # the suggestions
    store.diagramSuggest = lambda **kwds: qed.ux.store.diagramSuggest(store, **kwds)
    # the invocation of a method
    store.diagramInvoke = lambda **kwds: qed.ux.store.diagramInvoke(store, **kwds)
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


# the driver
def test() -> None:
    """
    Pick a dataset of a GSLC product on a diagram
    """
    # make a store
    store = storeOf()
    # its playground
    playground = store.playground()
    # with a GSLC reader and a picker
    store.diagramAdd(diagram=playground.relay, family="qed.readers.nisar.gslc", position=(0, 0, 0))
    (reader,) = playground.factories
    store.diagramAdd(diagram=playground.relay, family="pyre.viz.pickers.match", position=(8, 0, 0))
    (picker,) = [entity for entity in playground.factories if entity is not reader]
    # bound through their contents
    store.diagramMove(
        diagram=playground.relay,
        node=slotOf(reader, "contents").relay,
        position=slotOf(picker, "contents").position,
    )
    # both instances
    tag = uuid.uuid1().hex[:8]
    playground.pin(entity=reader, pin=qed.readers.nisar.gslc(name=f"gslc_{tag}", uri=gslc))
    playground.pin(entity=picker, pin=qed.viz.pickers.match()(name=f"match_{tag}"))
    # the requests to the picker
    request = {"diagram": playground.relay, "node": picker.relay}

    # making the dataset with an empty selection
    _, result, error, refusal = store.diagramInvoke(**request, method="pyre_make")
    # is refused, as the product and the reason
    assert result is None and error is None, (result, error)
    assert refusal["product"] == "dataset", refusal
    assert refusal["reason"] == "the selection names no band, frequency or polarization", refusal

    # the selections the picker suggests
    closed, selections, trait = store.diagramSuggest(**request, trait="selection")
    # are open, one per dataset of the product
    assert closed is False and len(selections) == 4, selections
    # and read the way the trait reads a map
    text, *_ = [
        qed.gql.diagram.FlowSuggestions.FlowSuggestions.describe(value=value, trait=trait).value
        for value in selections
    ]
    assert text == "band:L, frequency:A, polarization:HH", text

    # taking one
    _, error = store.diagramConfigure(**request, trait="selection", value=text)
    assert error is None, error
    # shows it on the diagram the way it was typed
    shown = qed.gql.diagram.FlowFactory.FlowFactory.render(
        value=picker.node.pin.selection, trait=trait
    )
    assert shown == text, shown
    # makes the dataset
    _, _, error, refusal = store.diagramInvoke(**request, method="pyre_make")
    assert error is None and refusal is None, (error, refusal)
    dataset = picker.node.pin.dataset
    assert dataset.selector == {"band": "L", "frequency": "A", "polarization": "HH"}

    # the credentials of the reader are a secret map
    _, error = store.diagramConfigure(
        diagram=playground.relay, node=reader.relay, trait="credentials", value="key=value"
    )
    # which the diagram never edits
    assert error, error

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
