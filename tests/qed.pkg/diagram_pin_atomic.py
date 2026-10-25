#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Pinning a factory of a diagram in place is all or nothing: a pin the recipe refuses, and one
that brings a slot the factory has no place for, both raise and leave the diagram and its recipe
exactly as they were
"""

# externals
import importlib
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
        pyre_name=f"diagram_pin_atomic.{uuid.uuid1()}", _playground=None, _viewports=[]
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


# everything a pin could change
def snapshot(diagram) -> tuple:
    """
    Record the state of {diagram} and its recipe that a pin touches
    """
    # the only factory
    (factory,) = diagram.factories
    # the state
    return (
        # the nodes the diagram knows
        frozenset(diagram.nodes),
        # where its slots are
        frozenset(slot.position for slot in diagram.slots),
        # what its labels say, part by part
        sorted(
            (
                (label.category, label.given, label.family, label.role, tuple(label.traits))
                for label in diagram.labels
            ),
            key=repr,
        ),
        # the slots of the factory
        frozenset(id(slot) for slot in factory.slots),
        # its arity
        (factory.inputs, factory.outputs),
        # what its recipe node is pinned to
        factory.node.pin,
        # the bindings of the recipe
        tuple(sorted(str(binding) for binding in diagram.recipe.bindings)),
        # and its products
        tuple(sorted(product.name for product in diagram.recipe.products())),
    )


# the driver
def test() -> None:
    """
    Pin an operator, then try two pins that must be refused, and check nothing moved
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
    # pin it to amplitude, so it has slots to lose
    _, amplitude = store.implementer(family="pyre.viz.operators.amplitude")
    # and pin the factory to it directly
    playground.pin(entity=factory, pin=amplitude)
    # record the state
    before = snapshot(diagram=playground)
    # it has slots
    assert len(playground.slots) == 2

    # a class of another protocol is refused by the recipe
    _, gray = store.implementer(family="pyre.viz.colormaps.gray")
    # so asking for it
    try:
        # directly, past the check the store makes
        playground.pin(entity=factory, pin=gray)
        # must fail
        assert False, "a pin of another protocol was accepted"
    # with the recipe's complaint
    except qed.flow.exceptions.RecipeError:
        # as expected
        pass
    # and nothing moved
    assert snapshot(diagram=playground) == before

    # a factory that finds no place for a slot of its new pin
    module = importlib.import_module("qed.ux.diagram.Factory")
    # is simulated by a factory that never finds a place for anything
    home = module.Factory.home
    # and install it in place of the real one
    module.Factory.home = lambda self, trait: None
    # so pinning to a class with a slot the factory does not have yet
    _, add = store.implementer(family="pyre.viz.operators.add")
    # when asked for directly
    try:
        # pin
        playground.pin(entity=factory, pin=add)
        # must fail
        assert False, "a pin with an unplaceable slot was accepted"
    # with the diagram's complaint
    except qed.exceptions.UnplaceableSlotError as error:
        # which names the factory and the trait
        assert error.factory == factory.node.name and error.trait, error
    # put the placement back
    finally:
        # as it was
        module.Factory.home = home
    # and nothing moved, the recipe included
    assert snapshot(diagram=playground) == before
    # with the placement back, the same pin goes through
    playground.pin(entity=factory, pin=add)
    # and changes the factory
    assert snapshot(diagram=playground) != before
    # into one with two inputs and one output
    assert (factory.inputs, factory.outputs) == (2, 1)
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
