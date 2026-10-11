#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Pin a protocol of the palette to each of its classes through the schema, and check that the
factory ends up the way it would be had the class been dropped from the palette directly: named
after the class, with the same slots
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
        pyre_name=f"diagram_pin_palette.{uuid.uuid1()}", _playground=None, _viewports=[]
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


# what the playground shows of its factories, slots and labels
reading = """
    query {
        qed {
            playground {
                factories { id family level inputs outputs }
                slots { id }
                labels { value category }
            }
        }
    }
"""
# the pin of a factory
pinning = """
    mutation ($payload: DiagramPinInput!) {
        diagramPin(input: $payload) {
            diagram { id }
        }
    }
"""


# run a document against the schema on behalf of {store}
def run(store: types.SimpleNamespace, document: str, variables: dict | None = None) -> dict:
    """
    Execute {document} with {store} as the context and hand back its data
    """
    # execute
    result = qed.gql.schema.execute(document, context={"store": store}, variables=variables)
    # there must be no errors
    assert not result.errors, result.errors
    # hand back the data
    return result.data


# what a playground with a single factory shows of it
def summary(store: types.SimpleNamespace) -> tuple:
    """
    Read the playground of {store} back and boil its only factory down to what a user sees
    """
    # read
    view = run(store, reading)["qed"]["playground"]
    # there is exactly one factory
    (factory,) = view["factories"]
    # and its label
    (label,) = [label["value"] for label in view["labels"] if label["category"] == "factory"]
    # what it is, what it says it is, and how many slots it has
    return (
        factory["family"],
        factory["level"],
        label,
        factory["inputs"],
        factory["outputs"],
        len(view["slots"]),
    )


# the driver
def test() -> None:
    """
    Pin each protocol of the palette to each of its classes and compare with a direct drop
    """
    # the protocols on offer
    palette = storeOf().palette()
    # count the classes, so an empty palette does not pass silently
    classes = 0
    # go through them
    for protocol in palette:
        # and through their classes
        for _, _, implementer in protocol.pyre_locateAllImplementers(namespace="pyre"):
            # the family the fan asks for
            family = implementer.pyre_family()
            # a class with no family cannot be asked for
            if not family:
                # so skip it
                continue
            # one more
            classes += 1
            # drop the protocol on a playground of its own
            pinned = storeOf()
            # at the origin
            pinned.diagramAdd(
                diagram=pinned.playground().relay,
                family=protocol.pyre_family(),
                position=(0, 0, 0),
            )
            # find its factory
            (factory,) = run(pinned, reading)["qed"]["playground"]["factories"]
            # pin it to the class
            run(
                pinned,
                pinning,
                {
                    "payload": {
                        "diagram": pinned.playground().relay,
                        "node": factory["id"],
                        "family": family,
                    }
                },
            )
            # drop the class itself on another playground
            dropped = storeOf()
            # at the same spot
            dropped.diagramAdd(
                diagram=dropped.playground().relay, family=family, position=(0, 0, 0)
            )
            # the two must look the same
            assert summary(pinned) == summary(dropped), (
                family,
                summary(pinned),
                summary(dropped),
            )
            # and the pinned one is the class
            assert summary(pinned)[:3] == (family, "class", [family.split(".")[-1]]), family
    # there must have been some
    assert classes > 0
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
