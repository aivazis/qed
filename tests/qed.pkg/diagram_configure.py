#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Changing a setting of a factory of a diagram: a factory pinned to a class is pinned to a new
instance of its class, under the name it was given, if any, carrying the new value; a factory
can also be pinned to a new instance directly, even from its protocol; the label of an instance
carries its given name, empty when nobody gave it one, and its class; a name that an instance of
the class goes by already pins the factory to that instance; one pinned to an instance has the
value changed, components included, which are given by name; every change is noted as made
interactively; a map is given by its entries; values the trait cannot take, maps whose entries
cannot be read, settings the class does not have, and names of components of other classes are
refused, leaving everything as it was
"""

# externals
import types
import uuid

# support
import pyre
import qed


# a component that is no reader, whose name no reader can take
class Stranger(qed.component, family="qed.tests.diagram.stranger"):
    """
    A component of a class that has nothing to do with readers
    """


# a store stand-in with an empty playground
def storeOf() -> types.SimpleNamespace:
    """
    Make a store with no playground yet and no views
    """
    # the store, under a name of its own: pyre hands back the old instance for a name it has
    # seen before
    store = types.SimpleNamespace(
        pyre_name=f"diagram_configure.{uuid.uuid1()}", _playground=None, _viewports=[]
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
    # the change of a setting
    store.diagramConfigure = lambda **kwds: qed.ux.store.diagramConfigure(store, **kwds)
    # which assigns the value through the store's helper
    store._configure = lambda **kwds: qed.ux.store._configure(store, **kwds)
    # and reads maps through another
    store._mapping = lambda **kwds: qed.ux.store._mapping(store, **kwds)
    # with the priorities of the executive
    store.pyre_executive = qed.ux.store.pyre_executive
    # the pin to a new instance
    store.diagramInstantiate = lambda **kwds: qed.ux.store.diagramInstantiate(store, **kwds)
    # which both make through the store's helper
    store._instantiate = lambda **kwds: qed.ux.store._instantiate(store, **kwds)
    # hand it off
    return store


# the driver
def test() -> None:
    """
    Walk a reader from its class to an instance through a change of setting, then change it
    """
    # make a store
    store = storeOf()
    # its playground
    playground = store.playground()
    # with a reader on it
    store.diagramAdd(diagram=playground.relay, family="pyre.viz.readers", position=(0, 0, 0))
    # find it
    (factory,) = playground.factories
    # the request, short of what changes
    request = {"diagram": playground.relay, "node": factory.relay}

    # a factory pinned to its protocol has no settings to change
    _, error = store.diagramConfigure(**request, trait="offset", value="12")
    # so it is refused
    assert error and factory.node.level == "protocol", error

    # pin it to the flat reader
    store.diagramPin(**request, family="qed.readers.native.flat")
    # its class
    flat = factory.node.pin
    # a value the trait cannot take
    _, error = store.diagramConfigure(**request, trait="offset", value="twelve", name="x")
    # is refused, and the factory stays pinned to its class
    assert error and factory.node.pin is flat, error
    # a map whose entries cannot be read
    _, error = store.diagramConfigure(**request, trait="selections", value="band", name="x")
    # is refused
    assert error and factory.node.pin is flat, error
    # a setting the class does not have
    _, error = store.diagramConfigure(**request, trait="nothing", value="1", name="x")
    # is refused
    assert error and factory.node.pin is flat, error
    # a name nobody uses
    name = f"configured_{uuid.uuid1().hex[:8]}"
    # with the good value
    _, error = store.diagramConfigure(**request, trait="offset", value="12", name=name)
    # goes through
    assert error is None, error
    # the factory is pinned to an instance of its class, under that name
    instance = factory.node.pin
    # it is an instance of the flat reader
    assert factory.node.level == "instance" and isinstance(instance, flat)
    # under the name it was given
    assert instance.pyre_name == name
    # which carries the new value
    assert instance.offset == 12
    # and the label says so
    (label,) = factory.labels
    # naming the instance and its class
    assert (label.given, label.family) == (name, "qed.readers.native.flat"), label.given

    # the value was set the way an edit is: noted as interactive
    _, locator = instance.pyre_getTrait(alias="offset")
    # so its locator says the flow editor set it
    assert str(locator) == "set interactively in the flow editor", str(locator)

    # once it is an instance, a change needs no name
    _, error = store.diagramConfigure(**request, trait="offset", value="24")
    # and goes through
    assert error is None and instance.offset == 24, error
    # a value it cannot take
    _, error = store.diagramConfigure(**request, trait="offset", value="lots")
    # is refused, and leaves the value as it was
    assert error and instance.offset == 24, error

    # a component is given by its name, the way a configuration file gives it
    _, error = store.diagramConfigure(**request, trait="cell", value="c16")
    # and the framework makes it
    assert error is None and instance.cell.spec == "qed.datatypes.complex128", error
    # a key of a map given on the command line
    executive = pyre.executive
    # goes into the configuration store with the priority of the command line
    executive.nameserver.insert(
        name=f"{name}.selections.band",
        value="0",
        priority=executive.priority.command(),
        locator=pyre.tracking.command(arg=f"--{name}.selections.band=0"),
    )
    # gives way to an edit of the whole map that follows it, given by its entries, the way it is
    # typed
    _, error = store.diagramConfigure(**request, trait="selections", value="band=1, layer=x")
    # and becomes a map
    assert error is None and dict(instance.selections) == {"band": "1", "layer": "x"}, error
    # or the way the diagram shows it
    _, error = store.diagramConfigure(**request, trait="selections", value="{band: 2}")
    # just the same
    assert error is None and dict(instance.selections) == {"band": "2"}, error

    # another reader, pinned to the same class
    store.diagramAdd(diagram=playground.relay, family="qed.readers.native.flat", position=(0, 8, 0))
    # find it
    (other,) = [entity for entity in playground.factories if entity is not factory]
    # a component of another class
    stranger = Stranger(name=f"stranger_{uuid.uuid1().hex[:8]}")
    # lends its name to no reader
    _, error = store.diagramConfigure(
        diagram=playground.relay,
        node=other.relay,
        trait="offset",
        value="1",
        name=stranger.pyre_name,
    )
    # so it is refused, and leaves the factory pinned to its class
    assert error and other.node.level == "class", error
    # a change with no name at all
    _, error = store.diagramConfigure(
        diagram=playground.relay, node=other.relay, trait="offset", value="1"
    )
    # makes an instance nobody named
    assert error is None and other.node.level == "instance", error
    # which reads as an instance of its class with an empty name
    (label,) = other.labels
    # with no name, and its class
    assert (label.given, label.family) == ("", "qed.readers.native.flat"), label.given

    # a reader pinned only to its protocol
    store.diagramAdd(diagram=playground.relay, family="pyre.viz.readers", position=(0, 16, 0))
    # find it
    (third,) = [e for e in playground.factories if e is not factory and e is not other]
    # can go all the way to an instance in one move
    _, error = store.diagramInstantiate(
        diagram=playground.relay, node=third.relay, family="qed.readers.native.envi", name="hdr"
    )
    # which goes through
    assert error is None and third.node.level == "instance", error
    # and reads as its name and its class
    (label,) = third.labels
    # the name it was given, and the envi reader
    assert (label.given, label.family) == ("hdr", "qed.readers.native.envi"), label.given
    # the instance it is pinned to
    hdr = third.node.pin
    # another reader, pinned only to its protocol
    store.diagramAdd(diagram=playground.relay, family="pyre.viz.readers", position=(0, 24, 0))
    # find it
    (fourth,) = [e for e in playground.factories if e not in (factory, other, third)]
    # asking for an envi reader by the name of the one there is
    _, error = store.diagramInstantiate(
        diagram=playground.relay, node=fourth.relay, family="qed.readers.native.envi", name="hdr"
    )
    # pins it to that very instance, the way a reader the configuration attached is reached
    assert error is None and fourth.node.pin is hdr, error
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
