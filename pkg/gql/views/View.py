# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node

# my parts
from ..datasets.Channel import Channel
from ..datasets.Dataset import Dataset
from ..readers.Reader import Reader
from ..readers.Selector import Selector
from ..readers.SelectorAxis import SelectorAxis
from .ViewMeasure import ViewMeasure
from .ViewSync import ViewSync
from .ViewZoom import ViewZoom


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
    name = graphene.String(required=True)
    session = graphene.String(required=True)
    # dataset selection
    selections = graphene.List(Selector)
    # visualization pipeline
    reader = graphene.Field(Reader)
    dataset = graphene.Field(Dataset)
    channel = graphene.Field(Channel)
    # dataset specific configuration
    measure = graphene.Field(ViewMeasure)
    sync = graphene.Field(ViewSync)
    zoom = graphene.Field(ViewZoom)
    # the per-member participation mask, if the reader is a stack
    members = graphene.List(graphene.NonNull(graphene.Boolean))
    # the available selector values, reflecting any pinned member
    available = graphene.List(SelectorAxis)

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
        Make a name
        """
        # easy enough
        return view.pyre_name

    @staticmethod
    def resolve_selections(view, info, **kwds):
        """
        Resolve the table of selector candidates
        """
        # easy enough
        return view.selections.items()

    @staticmethod
    def resolve_members(view, info, **kwds):
        """
        Resolve the per-member participation mask, if the reader is a stack
        """
        # hand it off
        return view.members

    @staticmethod
    def resolve_available(view, info, **kwds):
        """
        Resolve the available selector values, reflecting any pinned stack member
        """
        # hand off the effective availability
        return view.availableSelectors().items()


# end of file
