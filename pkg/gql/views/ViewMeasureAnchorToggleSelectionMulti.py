# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorToggleSelectionMultiInput import (
    ViewMeasureAnchorToggleSelectionMultiInput,
)

# the result types
from .ViewMeasure import ViewMeasure


# toggle the anchor selection in multinode mode
class ViewMeasureAnchorToggleSelectionMulti(graphene.Mutation):
    """
    Toggle the anchor selection in multinode mode
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorToggleSelectionMultiInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle the anchor selection in multinode mode
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorToggleSelectionMulti(
            viewport=input.viewport, index=input.index
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
