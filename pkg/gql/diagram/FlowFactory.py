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
        Get the family of the factory
        """
        # the flow factory behind the diagram entity knows
        return factory.factory.pyre_family()

    @staticmethod
    def resolve_doc(factory, info, **kwds):
        """
        Get the documentation of the factory
        """
        # it is the docstring of its class, with the indentation of the source removed
        return inspect.cleandoc(type(factory.factory).__doc__ or "")

    @staticmethod
    def resolve_traits(factory, info, **kwds):
        """
        Describe the slots and settings of the factory, in the order it declares them
        """
        # get the flow factory behind the diagram entity
        flow = factory.factory
        # the identities of its slots, by direction; traits overload their comparison operators,
        # so membership is decided by identity
        inputs = {id(trait) for trait in flow.pyre_inputTraits}
        outputs = {id(trait) for trait in flow.pyre_outputTraits}
        # the descriptions
        traits = []
        # go through its configurable traits
        for trait in flow.pyre_configurables():
            # decide what the trait is to the factory
            kind = (
                "input" if id(trait) in inputs else "output" if id(trait) in outputs else "setting"
            )
            # get its current value
            value = flow.pyre_inventory[trait].value
            # a slot holds a product, which is best described by its family
            if kind != "setting":
                # so describe it that way, if there is one
                value = None if value is None else value.pyre_family()
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
        x, y = factory.position
        # turn it into a point and return it
        return Point(x=x, y=y)


# end of file
