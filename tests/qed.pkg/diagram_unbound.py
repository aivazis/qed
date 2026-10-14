#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
A picker on a diagram whose contents nobody made: making its dataset fails, and the diagram is
told why without where in the framework the failure was raised from
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
        pyre_name=f"diagram_unbound.{uuid.uuid1()}", _playground=None, _viewports=[]
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
    # the invocation of a method
    store.diagramInvoke = lambda **kwds: qed.ux.store.diagramInvoke(store, **kwds)
    # hand it off
    return store


# the driver
def test() -> None:
    """
    Make the dataset of a picker that has nothing to pick from
    """
    # make a store
    store = storeOf()
    # its playground
    playground = store.playground()
    # with a picker
    store.diagramAdd(diagram=playground.relay, family="pyre.viz.pickers.match", position=(0, 0, 0))
    (picker,) = playground.factories
    # pinned to an instance, with nothing bound to its contents
    playground.pin(entity=picker, pin=qed.viz.pickers.match()(name=f"match_{uuid.uuid1().hex[:8]}"))

    # making its dataset
    _, result, error, refusal = store.diagramInvoke(
        diagram=playground.relay, node=picker.relay, method="pyre_make"
    )
    # fails, and is no refusal by the picker
    assert result is None and refusal is None, (result, refusal)
    # the diagram is told which input holds nothing
    assert error.endswith("has no product in 'contents'"), error
    # but not where the framework raised it
    assert "file=" not in error and "line=" not in error, error

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
