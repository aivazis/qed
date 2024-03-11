# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from .Node import Node

# my parts
from .ChannelMeasure import ChannelMeasure
from .ChannelSync import ChannelSync
from .ChannelZoom import ChannelZoom


# my node type
class ChannelView(graphene.ObjectType):
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
    measure = graphene.Field(ChannelMeasure)
    sync = graphene.Field(ChannelSync)
    zoom = graphene.Field(ChannelZoom)

    # resolvers
    @staticmethod
    def resolve_id(view, *_):
        """
        Get the {view} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{view.pyre_family()}:{view.pyre_name}"

    @staticmethod
    def resolve_name(view, *_):
        """
        Get the name of the view
        """
        # easy enough
        return view.pyre_name


# end of file
