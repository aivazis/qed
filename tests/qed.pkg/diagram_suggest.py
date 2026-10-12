#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Suggesting values for a setting of a factory of a diagram: a component is one of the classes that
implement the protocol of its trait, each once, in the order their package publishes them; the
shape of a flat reader is one of the ways the cells of its file can be arranged, once it is an
instance that knows its file and its cell; a reader whose header has the last word on its shape
has no guesses for it; settings the diagram cannot change get no suggestions at all
"""

# externals
import os
import types
import uuid

# support
import qed

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
        pyre_name=f"diagram_suggest.{uuid.uuid1()}", _playground=None, _viewports=[]
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
    # the suggestions
    store.diagramSuggest = lambda **kwds: qed.ux.store.diagramSuggest(store, **kwds)
    # which list the classes of a protocol through the store's helper
    store._implementers = lambda **kwds: qed.ux.store._implementers(store, **kwds)
    # hand it off
    return store


# the driver
def test() -> None:
    """
    Ask for suggestions for the settings of a flat reader, as a class and as an instance
    """
    # make a store
    store = storeOf()
    # its playground
    playground = store.playground()
    # with a flat reader on it
    store.diagramAdd(diagram=playground.relay, family="qed.readers.native.flat", position=(0, 0, 0))
    # find it
    (factory,) = playground.factories
    # the request, short of the setting
    request = {"diagram": playground.relay, "node": factory.relay}

    # the cell is a component
    closed, cells = store.diagramSuggest(**request, trait="cell")
    # so its suggestions are the datatypes, and nothing else
    assert closed is True
    # each once
    families = [cell.pyre_family() for cell in cells]
    assert len(families) == len(set(families)), families
    # in the order their package publishes them
    assert families[0] == "qed.datatypes.char", families
    assert families[-1] == "qed.datatypes.complex128", families

    # the shape of a class
    closed, shapes = store.diagramSuggest(**request, trait="shape")
    # has no guesses, since a class has no file
    assert closed is False and shapes == [], shapes
    # and a setting the diagram cannot change
    assert store.diagramSuggest(**request, trait="selections") is None

    # pin it to an instance that knows its file and its cell
    playground.pin(
        entity=factory,
        pin=qed.readers.native.flat(name=f"suggest_{uuid.uuid1().hex[:8]}", uri=raster, cell="c16"),
    )
    # the shape
    closed, shapes = store.diagramSuggest(**request, trait="shape")
    # is open
    assert closed is False
    # and the arrangements of its cells include the right one
    assert (65, 65) in shapes, shapes
    # every one of them holds all the cells
    assert all(lines * samples == 65 * 65 for lines, samples in shapes), shapes

    # an envi reader on its own
    store.diagramAdd(diagram=playground.relay, family="qed.readers.native.envi", position=(0, 8, 0))
    # find it
    (envi,) = [entity for entity in playground.factories if entity is not factory]
    # pinned to an instance over the same file
    playground.pin(
        entity=envi,
        pin=qed.readers.native.envi(name=f"suggest_{uuid.uuid1().hex[:8]}", uri=raster, cell="c16"),
    )
    # has no guesses for its shape, which its header decides
    closed, shapes = store.diagramSuggest(diagram=playground.relay, node=envi.relay, trait="shape")
    assert closed is False and shapes == [], shapes
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
