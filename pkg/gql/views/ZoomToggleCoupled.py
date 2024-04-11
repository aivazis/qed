# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# response types
from .Zoom import Zoom


# toggle the zoom lock flag
class ZoomToggleCoupled(graphene.Mutation):
    """
    Toggle the zoom lock flag
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)

    # the result is the updated view
    zoom = graphene.List(Zoom)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Set the zoom level for {viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        zoom = store.zoomToggleCoupled(viewport=viewport)
        # form the mutation resolution context
        context = {"zoom": zoom}
        # and resolve the mutation
        return context


# end of file
