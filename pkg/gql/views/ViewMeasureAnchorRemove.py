# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorRemoveInput import ViewMeasureAnchorRemoveInput

# the result types
from .ViewMeasure import ViewMeasure


# remove an anchor from the pile
class ViewMeasureAnchorRemove(graphene.Mutation):
    """
    Remove an anchor from the pile
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorRemoveInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Remove an anchor from the pile
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAnchorRemove(
            viewport=input.viewport, anchor=input.anchor
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
