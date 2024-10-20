# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node


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
    name = graphene.String(required=True)
    family = graphene.String(required=True)

    # resolvers
    @staticmethod
    def resolve_id(factory, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {factory}
        return f"{factory.pyre_family()}:{factory.pyre_name}"

    @staticmethod
    def resolve_name(factory, info, **kwds):
        """
        Make a name
        """
        # easy enough
        return factory.pyre_name

    @staticmethod
    def resolve_family(factory, info, **kwds):
        """
        Make a name
        """
        # easy enough
        return f"{factory.pyre_family()}"


# end of file
