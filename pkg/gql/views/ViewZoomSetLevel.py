# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewZoomSetLevelInput import ViewZoomSetLevelInput

# the result types
from .ViewZoom import ViewZoom


# set the zoom level
class ViewZoomSetLevel(graphene.Mutation):
    """
    Set the zoom level
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewZoomSetLevelInput(required=True)

    # the result is the affected zoom states
    zooms = graphene.List(ViewZoom)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Set the zoom level for {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # set the zoom level
        zooms = store.zoomSetLevel(
            viewport=input.viewport,
            horizontal=input.horizontal,
            vertical=input.vertical,
        )
        # form the mutation resolution context
        context = {"zooms": zooms}
        # and resolve the mutation
        return context


# end of file
