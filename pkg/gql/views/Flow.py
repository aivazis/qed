# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node


# my node type
class Flow(graphene.ObjectType):
    """
    The store managed state of a dataset channel
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.ID()

    dirty = graphene.Boolean()
    active = graphene.Boolean()

    # resolvers
    @staticmethod
    def resolve_id(flow, *_):
        """
        Get the {flow} id
        """
        # splice together the {family} and {name} of the {flow}
        return f"{flow.pyre_family()}:{flow.pyre_name}.flow"

    @staticmethod
    def resolve_name(flow, *_):
        """
        Get the name of the {flow}
        """
        # easy enough
        return f"{flow.pyre_name}.flow"


# end of file
