# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# response types
from .Zoom import Zoom


# set the zoom level
class ZoomSetLevel(graphene.Mutation):
    """
    Set the zoom level
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        horizontal = graphene.Float(required=True)
        vertical = graphene.Float(required=True)

    # the result is the updated view
    zoom = graphene.List(Zoom)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, horizontal, vertical):
        """
        Set the zoom level for {viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        zoom = store.zoomSetLevel(
            viewport=viewport, horizontal=horizontal, vertical=vertical
        )
        # form the mutation resolution context
        context = {"zoom": zoom}
        # and resolve the mutation
        return context


# end of file
