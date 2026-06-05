# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorToggleSelectionInput import ViewMeasureAnchorToggleSelectionInput

# the result types
from .ViewMeasure import ViewMeasure


# toggle the anchor selection in single node mode
class ViewMeasureAnchorToggleSelection(graphene.Mutation):
    """
    Toggle the anchor selection in single node mode
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorToggleSelectionInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle the anchor selection in single node mode
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorToggleSelection(
            viewport=input.viewport, index=input.index
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
