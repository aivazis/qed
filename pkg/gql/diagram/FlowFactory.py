# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections.abc
import graphene
import inspect

# support
import qed

# my interface
from ..Node import Node

# field types
from .FlowMethod import FlowMethod
from .FlowTrait import FlowTrait
from .Point import Point


# the type
class FlowFactory(graphene.ObjectType):
    """
    A product factory
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    # the family of the factory, which says what it does
    family = graphene.String(required=True)
    # the family of the protocol it satisfies, which names the classes it can be pinned to
    protocol = graphene.String(required=True)
    # how far down it is pinned: "protocol", "class", or "instance"
    level = graphene.String(required=True)
    # its documentation
    doc = graphene.String()
    # its slots and settings
    traits = graphene.List(graphene.NonNull(FlowTrait), required=True)
    # the methods the diagram can invoke
    methods = graphene.List(graphene.NonNull(FlowMethod), required=True)
    # product counts
    inputs = graphene.Int(required=True)
    outputs = graphene.Int(required=True)
    # placements
    at = graphene.Field(Point, required=True)

    # resolvers
    @staticmethod
    def resolve_id(factory, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {factory}
        return factory.relay

    @staticmethod
    def resolve_family(factory, info, **kwds):
        """
        Get the family of the factory: the one of its pin, or else the one of its protocol
        """
        # get the recipe node behind the diagram entity
        node = factory.node
        # the family of whatever is most specific about it
        family = (node.protocol if node.pin is None else node.pin).pyre_family()
        # a protocol that is a building block has none
        return family or ""

    @staticmethod
    def resolve_protocol(factory, info, **kwds):
        """
        Get the family of the protocol the factory satisfies
        """
        # a protocol that is a building block has none
        return factory.node.protocol.pyre_family() or ""

    @staticmethod
    def resolve_level(factory, info, **kwds):
        """
        Get how far down the factory is pinned
        """
        # the recipe node behind the diagram entity knows
        return factory.node.level

    @staticmethod
    def resolve_doc(factory, info, **kwds):
        """
        Get the documentation of the factory
        """
        # get the recipe node behind the diagram entity
        node = factory.node
        # the class that documents it: its protocol, the class it is pinned to, or the class of
        # the instance it is pinned to
        source = (
            node.protocol
            if node.pin is None
            else node.pin if isinstance(node.pin, type) else type(node.pin)
        )
        # it is the docstring of that class, with the indentation of the source removed
        return inspect.cleandoc(source.__doc__ or "")

    @staticmethod
    def resolve_traits(factory, info, **kwds):
        """
        Describe the slots and settings of the factory, in the order it declares them
        """
        # get the recipe node behind the diagram entity
        node = factory.node
        # the traits are declared by its pin, or else by its protocol
        source = node.protocol if node.pin is None else node.pin
        # the identities of its slots, by direction; traits overload their comparison operators,
        # so membership is decided by identity
        inputs = {id(trait) for trait in node.inputs}
        outputs = {id(trait) for trait in node.outputs}
        # the descriptions
        traits = []
        # go through its configurable traits
        for trait in source.pyre_configurables():
            # decide what the trait is to the factory
            kind = (
                "input" if id(trait) in inputs else "output" if id(trait) in outputs else "setting"
            )
            # get its current value: an instance has one for every trait
            if node.level == "instance":
                # in its inventory
                value = node.pin.pyre_inventory[trait].value
                # a slot holds a product, which is best described by its family
                if kind != "setting":
                    # so describe it that way, if there is one
                    value = None if value is None else value.pyre_family()
            # a class has the settings it will be made with
            elif node.level == "class" and kind == "setting":
                # which the node keeps when they are given, or else the class has as configured
                value = node.settings.get(trait.name, getattr(node.pin, trait.name, None))
            # otherwise, the settings it will be made with
            else:
                # are kept by the node
                value = node.settings.get(trait.name)
            # a secret, e.g. credentials, never leaves the server
            if trait.secret:
                # so it is described without its value
                value = None
            # describe the trait
            traits.append(
                FlowTrait(
                    name=trait.name,
                    kind=kind,
                    type=trait.typename,
                    value=FlowFactory.render(value=value, trait=trait),
                    default=FlowFactory.default(trait=trait),
                    doc=trait.doc,
                    editable=factory.editable(trait=trait),
                )
            )
        # hand off the descriptions
        return traits

    @staticmethod
    def resolve_methods(factory, info, **kwds):
        """
        Describe the methods of the factory that the diagram can invoke
        """
        # get the recipe node behind the diagram entity
        node = factory.node
        # only an instance has methods to invoke
        invocable = node.level == "instance"
        # describe each one, by its name and the first line of its documentation
        return [
            FlowMethod(
                name=behavior.name,
                doc=(inspect.getdoc(behavior.pyre_method) or "").split("\n")[0] or None,
                invocable=invocable,
            )
            for behavior in factory.methods()
        ]

    @staticmethod
    def render(value, trait=None):
        """
        Render the {value} of a trait as text: a class of components by its family, e.g. the
        default of a trait of a class, a datatype by its spec, which is how it is configured, any
        other component by its family, a map of {trait} the way the trait reads one, and the
        rest the way they print
        """
        # a trait with no value
        if value is None:
            # has nothing to show
            return None
        # a map, when the trait that holds it is known
        if trait is not None and isinstance(value, collections.abc.Mapping):
            # reads as the text the trait makes it from, e.g. "band:L, frequency:A"
            return trait.string(value)
        # a class of components, whose instance properties, e.g. the spec of a datatype, mean
        # nothing yet
        if isinstance(value, type) and issubclass(value, qed.component):
            # reads as its family, the way it is configured
            return value.pyre_family()
        # a datatype
        if qed.protocols.datatype.pyre_isImplementedBy(value=value):
            # reads as its spec
            return value.spec
        # any other component
        if isinstance(value, qed.component):
            # reads as its family, or its name when it has none
            return value.pyre_family() or value.pyre_name
        # the rest print the way they are
        return str(value)

    @staticmethod
    def default(trait):
        """
        Render the default of {trait} as text, when it has one that reads as a value
        """
        # get the default
        default = trait.default
        # a default that is computed, e.g. the foundry of a slot, does not read as a value
        if default is None or callable(default):
            # so there is nothing to show
            return None
        # a map reads the way the trait reads one
        if isinstance(default, collections.abc.Mapping):
            # as its text
            return trait.string(default)
        # otherwise, render it
        return str(default)

    @staticmethod
    def resolve_at(factory, info, **kwds):
        """
        Resolve the factory position
        """
        # get the location
        x, y, z = factory.position
        # turn it into a point and return it
        return Point(x=x, y=y, z=z)


# end of file
