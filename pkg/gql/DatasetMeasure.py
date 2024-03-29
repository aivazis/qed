# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from .Node import Node

# my parts
from .Pixel import Pixel


# my node type
class DatasetMeasure(graphene.ObjectType):
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

    active = graphene.Boolean()
    path = graphene.List(Pixel)
    closed = graphene.Boolean()
    selection = graphene.List(graphene.Int)

    # resolvers
    @staticmethod
    def resolve_id(measure, *_):
        """
        Get the {measure} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{measure.pyre_family()}:{measure.pyre_name}"

    @staticmethod
    def resolve_name(measure, *_):
        """
        Get the name of the {measure}
        """
        # easy enough
        return measure.pyre_name


# end of file
