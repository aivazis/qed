# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal

# my interface
from ..Node import Node

# my parts
from .FlowConnector import FlowConnector
from .FlowFactory import FlowFactory
from .FlowLabel import FlowLabel
from .FlowSlot import FlowSlot


# the type
class FlowDiagram(graphene.ObjectType):
    """
    The visualization pipeline diagram
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    family = graphene.String(required=True)
    # diagram parts
    connectors = graphene.List(FlowConnector)
    factories = graphene.List(FlowFactory)
    labels = graphene.List(FlowLabel)
    slots = graphene.List(FlowSlot)

    # resolvers
    @staticmethod
    def resolve_id(diagram, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {diagram}
        return f"{diagram.pyre_family()}:{diagram.pyre_name}.diagram"

    @staticmethod
    def resolve_name(diagram, info, **kwds):
        """
        Make a name
        """
        # easy enough
        return f"{diagram.pyre_name}.diagram"

    @staticmethod
    def resolve_family(diagram, info, **kwds):
        """
        Make a name
        """
        # easy enough
        return f"{diagram.pyre_family()}"


# end of file
