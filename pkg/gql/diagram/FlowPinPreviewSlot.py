# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# field types
from .Point import Point


# a slot that a factory would gain if it were pinned to a class
class FlowPinPreviewSlot(graphene.ObjectType):
    """
    A slot that pinning a factory would add, with the trait it stands for and its spot
    """

    # the name of the trait
    trait = graphene.String(required=True)
    # whether the factory reads it
    input = graphene.Boolean(required=True)
    # whether it writes it
    output = graphene.Boolean(required=True)
    # where the slot would go
    at = graphene.Field(Point, required=True)

    # resolvers
    @staticmethod
    def resolve_trait(fresh, info, **kwds):
        """
        Get the name of the trait
        """
        # unpack
        trait, _ = fresh
        # and hand off its name
        return trait.name

    @staticmethod
    def resolve_input(fresh, info, **kwds):
        """
        Get whether the factory reads the slot
        """
        # unpack
        trait, _ = fresh
        # and ask the trait
        return bool(trait.input)

    @staticmethod
    def resolve_output(fresh, info, **kwds):
        """
        Get whether the factory writes the slot
        """
        # unpack
        trait, _ = fresh
        # and ask the trait
        return bool(trait.output)

    @staticmethod
    def resolve_at(fresh, info, **kwds):
        """
        Get where the slot would go
        """
        # unpack
        _, (x, y, z) = fresh
        # and make a point
        return Point(x=x, y=y, z=z)


# end of file
