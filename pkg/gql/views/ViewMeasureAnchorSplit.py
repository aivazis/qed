# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorSplitInput import ViewMeasureAnchorSplitInput

# the result types
from .ViewMeasure import ViewMeasure


# split in two the leg that starts at an anchor
class ViewMeasureAnchorSplit(graphene.Mutation):
    """
    Split in two the leg that starts at an anchor
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorSplitInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Split in two the leg that starts at an anchor
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorSplit(
            viewport=input.viewport, anchor=input.anchor
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
