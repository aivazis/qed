# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorExtendSelectionInput import ViewMeasureAnchorExtendSelectionInput

# the result types
from .ViewMeasure import ViewMeasure


# extend the anchor selection to a given anchor index
class ViewMeasureAnchorExtendSelection(graphene.Mutation):
    """
    Extend the anchor selection to a given anchor index
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorExtendSelectionInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Extend the anchor selection to a given anchor index
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorExtendSelection(
            viewport=input.viewport, index=input.index
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
