#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Pin a factory of the playground in place through the schema: a protocol becomes one of its
classes and takes the slots the class has, another class swaps them for its own, and pinning it
back to nothing leaves it with the slots of its protocol; a family of another protocol is
reported and changes nothing
"""

# externals
import types
import uuid

# support
import journal
import qed


# a store stand-in with an empty playground
def storeOf():
    """
    Make a store with no playground yet and no views
    """
    # the store, under a name of its own: pyre hands back the old instance for a name it has
    # seen before
    store = types.SimpleNamespace(
        pyre_name=f"diagram_pin.{uuid.uuid1()}", _playground=None, _viewports=[]
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
    # and the pin of a factory in place
    store.diagramPin = lambda **kwds: qed.ux.store.diagramPin(store, **kwds)
    # hand it off
    return store


# what the playground shows of its factories
reading = """
    query {
        qed {
            playground {
                factories { id family protocol level inputs outputs }
                slots { id }
                labels { given family role traits category }
            }
        }
    }
"""
# the pin of a factory
pinning = """
    mutation ($payload: DiagramPinInput!) {
        diagramPin(input: $payload) {
            diagram { factories { id family level } }
        }
    }
"""


# the driver
def test():
    """
    Drop an operator on the playground, pin it to amplitude, then to add, then back to nothing,
    and check its slots each time; then ask for a class of another protocol
    """
    # make a store
    store = storeOf()
    # the execution context
    context = {"store": store}

    # run a document against the schema
    def run(document, variables=None):
        """
        Execute {document} and hand back its data
        """
        # execute
        result = qed.gql.schema.execute(document, context=context, variables=variables)
        # there must be no errors
        assert not result.errors, result.errors
        # hand back the data
        return result.data

    # the playground
    playground = store.playground()
    # with an operator on it, which stands for any of them
    store.diagramAdd(
        diagram=playground.relay, family=qed.viz.operator.pyre_family(), position=(0, 0, 0)
    )
    # read it back
    view = run(reading)["qed"]["playground"]
    # one factory, at the protocol level, with no slots
    (factory,) = view["factories"]
    assert (factory["family"], factory["protocol"], factory["level"]) == (
        "pyre.viz.operators",
        "pyre.viz.operators",
        "protocol",
    )
    assert view["slots"] == []
    # the payload that pins it
    payload = {"diagram": playground.relay, "node": factory["id"]}

    # pin it to amplitude
    run(pinning, {"payload": {**payload, "family": "pyre.viz.operators.amplitude"}})
    # read it back
    view = run(reading)["qed"]["playground"]
    (factory,) = view["factories"]
    # it is the class now, with a signal in and an amplitude out
    assert (factory["family"], factory["level"]) == ("pyre.viz.operators.amplitude", "class")
    assert (factory["inputs"], factory["outputs"]) == (1, 1)
    assert len(view["slots"]) == 2
    # and its label, as the schema serves it, says so
    assert [
        (l["given"], l["family"], l["role"]) for l in view["labels"] if l["category"] == "factory"
    ] == [(None, "pyre.viz.operators.amplitude", "operator")]

    # pin it to add, which takes two inputs and makes one output
    run(pinning, {"payload": {**payload, "family": "pyre.viz.operators.add"}})
    view = run(reading)["qed"]["playground"]
    (factory,) = view["factories"]
    # its slots follow
    assert (factory["family"], factory["inputs"], factory["outputs"]) == (
        "pyre.viz.operators.add",
        2,
        1,
    )
    assert len(view["slots"]) == 3
    # and no two of them share a spot
    spots = [slot.position for slot in playground.slots]
    assert len(set(spots)) == len(spots)

    # back to nothing
    run(pinning, {"payload": payload})
    view = run(reading)["qed"]["playground"]
    (factory,) = view["factories"]
    # it is the protocol again, with its slots, which are none
    assert (factory["family"], factory["level"]) == ("pyre.viz.operators", "protocol")
    assert view["slots"] == []
    # and nothing is left over in the diagram's indices or the recipe
    assert set(playground.nodes) == {factory.eid for factory in playground.factories} | {
        label.eid for label in playground.labels
    }
    assert playground.recipe.bindings == []

    # a class of another protocol is reported, so quiet the report
    journal.warning("qed.ux.diagram").deactivate()
    # and asked for
    run(pinning, {"payload": {**payload, "family": "pyre.viz.colormaps.gray"}})
    # leaves the factory as it was
    (factory,) = run(reading)["qed"]["playground"]["factories"]
    assert factory["level"] == "protocol"
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
