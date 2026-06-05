# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorMoveInput import ViewMeasureAnchorMoveInput

# the result types
from .ViewMeasure import ViewMeasure


# move a measure handle by a pixel delta
class ViewMeasureAnchorMove(graphene.Mutation):
    """
    Move a measure handle by a pixel delta
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorMoveInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Move a measure handle by a pixel delta
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorMove(
            viewport=input.viewport, handle=input.handle, dx=input.dx, dy=input.dy
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
