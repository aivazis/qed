# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureAnchorAddInput import ViewMeasureAnchorAddInput

# the result types
from .ViewMeasure import ViewMeasure


# add an anchor to the measure path
class ViewMeasureAnchorAdd(graphene.Mutation):
    """
    Add an anchor to the measure path
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureAnchorAddInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Add an anchor to the measure path
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureAddAnchor(
            viewport=input.viewport, x=input.x, y=input.y, index=input.index
        )
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
