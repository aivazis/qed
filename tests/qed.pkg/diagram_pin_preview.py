#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
The preview of a pin describes what the pin does without doing it: the parts of the label the
factory gets, the slots it gains and where they go, and the slots it lets go of all match the pin
made right after, and the preview leaves the diagram as it was
"""

# externals
import types
import uuid

# support
import qed


# a store stand-in with an empty playground
def storeOf() -> types.SimpleNamespace:
    """
    Make a store with no playground yet and no views
    """
    # the store, under a name of its own: pyre hands back the old instance for a name it has
    # seen before
    store = types.SimpleNamespace(
        pyre_name=f"diagram_pin_preview.{uuid.uuid1()}", _playground=None, _viewports=[]
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
    # the pin of a factory in place
    store.diagramPin = lambda **kwds: qed.ux.store.diagramPin(store, **kwds)
    # and its preview
    store.diagramPinPreview = lambda **kwds: qed.ux.store.diagramPinPreview(store, **kwds)
    # hand it off
    return store


# the driver
def test() -> None:
    """
    Preview pins of an operator, and check each against the pin made right after
    """
    # make a store
    store = storeOf()
    # its playground
    playground = store.playground()
    # with an operator on it
    store.diagramAdd(
        diagram=playground.relay, family=qed.viz.operator.pyre_family(), position=(0, 0, 0)
    )
    # find it
    (factory,) = playground.factories
    # the classes to pin it to, one after the other: from the protocol to one input, then to
    # two, which keeps one slot and adds another, then back to one, which lets a slot go
    for family in [
        "pyre.viz.operators.amplitude",
        "pyre.viz.operators.add",
        "pyre.viz.operators.amplitude",
    ]:
        # the nodes and their spots before the preview
        before = {eid: node.position for eid, node in playground.nodes.items()}
        # preview the pin
        preview = store.diagramPinPreview(
            diagram=playground.relay, node=factory.relay, family=family
        )
        # there is one
        assert preview is not None, family
        # and asking for it changed nothing
        assert {eid: node.position for eid, node in playground.nodes.items()} == before
        # the slots it says the factory lets go of
        dropped = {id(slot) for slot in preview["left"]}
        # the ones it says the factory gains, by trait, with their spots
        fresh = {trait.name: spot for trait, spot in preview["fresh"]}
        # the slots of the factory before the pin
        old = set(factory.slots)
        # now pin
        store.diagramPin(diagram=playground.relay, node=factory.relay, family=family)
        # the label has the parts promised: no given name, the family of the class, and the
        # role of the protocol
        (label,) = factory.labels
        promised = (None, preview["family"], preview["role"])
        assert (label.given, label.family, label.role) == promised, (label.family, promised)
        # the slots that went are the ones promised
        assert {id(slot) for slot in old - set(factory.slots)} == dropped, family
        # the slots that came are where they were promised
        gained = set(factory.slots) - old
        assert sorted(slot.position for slot in gained) == sorted(fresh.values()), family
    # a family that is not a class of the protocol has no preview
    assert (
        store.diagramPinPreview(
            diagram=playground.relay, node=factory.relay, family="pyre.viz.colormaps.gray"
        )
        is None
    )
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
