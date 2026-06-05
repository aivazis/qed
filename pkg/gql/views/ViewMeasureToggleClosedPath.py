# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureToggleClosedPathInput import ViewMeasureToggleClosedPathInput

# the result types
from .ViewMeasure import ViewMeasure


# toggle whether the measure path is closed
class ViewMeasureToggleClosedPath(graphene.Mutation):
    """
    Toggle whether the measure path is closed
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureToggleClosedPathInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle whether the measure path is closed
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureToggleClosedPath(viewport=input.viewport)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
