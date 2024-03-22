# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from .Node import Node

# my parts
from .Channel import Channel
from .Dataset import Dataset
from .Reader import Reader


# the type
class View(graphene.ObjectType):
    """
    The specification of what is visible in a given view
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    name = graphene.ID(required=True)
    # my parts
    reader = graphene.Field(Reader)
    dataset = graphene.Field(Dataset)
    channel = graphene.Field(Channel)

    # resolvers
    @staticmethod
    def resolve_id(view, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {view}
        return f"{view.pyre_family()}:{view.pyre_name}"

    @staticmethod
    def resolve_name(view, info, **kwds):
        """
        Make an id
        """
        # easy enough
        return view.pyre_name


# end of file
