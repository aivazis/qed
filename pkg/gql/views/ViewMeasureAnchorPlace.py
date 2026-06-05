# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorPlaceInput import ViewMeasureAnchorPlaceInput

# the result types
from .ViewMeasure import ViewMeasure


# place a measure handle at a pixel
class ViewMeasureAnchorPlace(graphene.Mutation):
    """
    Place a measure handle at a pixel
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorPlaceInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Place a measure handle at a pixel
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorPlace(
            viewport=input.viewport, handle=input.handle, x=input.x, y=input.y
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
