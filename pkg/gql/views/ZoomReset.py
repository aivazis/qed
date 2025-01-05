# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal


# response types
from .Zoom import Zoom


# reset the zoom state
class ZoomReset(graphene.Mutation):
    """
    Reset the zoom state back to its persisted value
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)

    # the result is the updated view
    zoom = graphene.Field(Zoom)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Reset the zoom state
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        zoom = store.zoomReset(viewport=viewport)
        # form the mutation resolution context
        context = {"zoom": zoom}
        # and resolve the mutation
        return context


# end of file
