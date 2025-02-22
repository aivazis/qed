# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my interface
from .Node import Node


# a controller that captures a range of values
class RangeController(graphene.ObjectType):
    """
    A controller that captures a range of values
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    # a flag that indicates the controller configuration has been modified
    # since last persisted
    dirty = graphene.Boolean()
    # payload
    slot = graphene.String()
    min = graphene.Float()
    max = graphene.Float()
    low = graphene.Float()
    high = graphene.Float()

    # resolvers
    @staticmethod
    def resolve_id(context, *_):
        # extract the controller
        controller = context["controller"]
        # form the controller id
        return controller.pyre_name

    @staticmethod
    def resolve_slot(context, *_):
        """
        Resolve the slot managed by this controller
        """
        # extract the controller metadata
        trait = context["trait"]
        # easy enough
        return trait.name

    @staticmethod
    def resolve_dirty(context, *_):
        """
        Check the controller state relative to its persisted configuration
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.dirty

    @staticmethod
    def resolve_min(context, *_):
        """
        Resolve the minimum value of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.min

    @staticmethod
    def resolve_max(context, *_):
        """
        Resolve the maximum value of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.max

    @staticmethod
    def resolve_low(context, *_):
        """
        Resolve the low end of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.low

    @staticmethod
    def resolve_high(context, *_):
        """
        Resolve the high end of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.high


# end of file
