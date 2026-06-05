# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewZoomResetInput import ViewZoomResetInput

# the result types
from .ViewZoom import ViewZoom


# reset the zoom state
class ViewZoomReset(graphene.Mutation):
    """
    Reset the zoom state back to its persisted value
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewZoomResetInput(required=True)

    # the result is the updated zoom state
    zoom = graphene.Field(ViewZoom)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Reset the zoom state of {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # reset the zoom state
        zoom = store.zoomReset(viewport=input.viewport)
        # form the mutation resolution context
        context = {"zoom": zoom}
        # and resolve the mutation
        return context


# end of file
