# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewZoomToggleCoupledInput import ViewZoomToggleCoupledInput

# the result types
from .ViewZoom import ViewZoom


# toggle whether the zoom axes are coupled
class ViewZoomToggleCoupled(graphene.Mutation):
    """
    Toggle whether horizontal and vertical zoom are coupled
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewZoomToggleCoupledInput(required=True)

    # the result is the affected zoom states
    zooms = graphene.List(ViewZoom)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle whether the zoom axes are coupled for {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # toggle the coupled flag
        zooms = store.zoomToggleCoupled(viewport=input.viewport)
        # form the mutation resolution context
        context = {"zooms": zooms}
        # and resolve the mutation
        return context


# end of file
