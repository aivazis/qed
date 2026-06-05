# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureToggleLayerInput import ViewMeasureToggleLayerInput

# the result types
from .ViewMeasure import ViewMeasure


# toggle a reader's participation in the measure layer
class ViewMeasureToggleLayer(graphene.Mutation):
    """
    Toggle a reader's participation in the measure layer
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureToggleLayerInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle a reader's participation in the measure layer
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.toggleMeasure(viewport=input.viewport, source=input.reader)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
