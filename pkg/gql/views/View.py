# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node

# my parts
from ..Channel import Channel
from ..Dataset import Dataset
from ..Reader import Reader
from ..Selector import Selector
from ..Selectors import Selectors
from .Measure import Measure
from .Sync import Sync
from .Zoom import Zoom


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
    session = graphene.String(required=True)
    # dataset selection
    selections = graphene.List(Selector)
    # visualization pipeline
    reader = graphene.Field(Reader)
    dataset = graphene.Field(Dataset)
    channel = graphene.Field(Channel)
    # dataset specific configuration
    measure = graphene.Field(Measure)
    sync = graphene.Field(Sync)
    zoom = graphene.Field(Zoom)
    # the pinned stack member, if any
    stackIndex = graphene.Int()
    # the available selector values, reflecting any pinned member
    available = graphene.List(Selectors)

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
    def resolve_stackIndex(view, info, **kwds):
        """
        Resolve the pinned stack member, if any
        """
        # hand it off
        return view.stackIndex

    @staticmethod
    def resolve_available(view, info, **kwds):
        """
        Resolve the available selector values, reflecting any pinned stack member
        """
        # hand off the effective availability
        return view.availableSelectors().items()


# end of file
