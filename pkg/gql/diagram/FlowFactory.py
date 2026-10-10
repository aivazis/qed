# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import inspect

# my interface
from ..Node import Node

# field types
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
    # how far down it is pinned: "protocol", "class", or "instance"
    level = graphene.String(required=True)
    # its documentation
    doc = graphene.String()
    # its slots and settings
    traits = graphene.List(graphene.NonNull(FlowTrait), required=True)
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
            # otherwise, the settings it will be made with
            else:
                # are kept by the node
                value = node.settings.get(trait.name)
            # describe the trait
            traits.append(
                FlowTrait(
                    name=trait.name,
                    kind=kind,
                    type=trait.typename,
                    value=None if value is None else str(value),
                    default=FlowFactory.default(trait=trait),
                    doc=trait.doc,
                )
            )
        # hand off the descriptions
        return traits

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
