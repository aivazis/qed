# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


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
        interfaces = Node,


    # my fields
    id = graphene.ID()
    # my session key; used to detect changes in the controller state
    session = graphene.ID()
    # payload
    slot = graphene.String()
    min = graphene.Float()
    max = graphene.Float()
    low = graphene.Float()
    high = graphene.Float()


    # resolvers
    def resolve_id(context, *_):
        # extract the controller
        controller = context["controller"]
        # form the controller id
        return controller.pyre_name


    def resolve_slot(context, *_):
        """
        Resolve the slot managed by this controller
        """
        # extract the controller metadata
        trait = context["trait"]
        # easy enough
        return trait.name


    def resolve_min(context, *_):
        """
        Resolve the minimum value of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.min


    def resolve_max(context, *_):
        """
        Resolve the maximum value of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.max


    def resolve_low(context, *_):
        """
        Resolve the low end of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.low


    def resolve_high(context, *_):
        """
        Resolve the high end of the range
        """
        # extract the controller
        controller = context["controller"]
        # easy enough
        return controller.high


# end of file
