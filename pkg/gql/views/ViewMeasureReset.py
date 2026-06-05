# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureResetInput import ViewMeasureResetInput

# the result types
from .ViewMeasure import ViewMeasure


# reset the measure state back to its persisted value
class ViewMeasureReset(graphene.Mutation):
    """
    Reset the measure state back to its persisted value
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureResetInput(required=True)

    # the result is the affected measure states, one per path-synced view
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Reset the measure state back to its persisted value
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureReset(viewport=input.viewport)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
