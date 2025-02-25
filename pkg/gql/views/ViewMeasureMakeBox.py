# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMeasureMakeBoxInput import ViewMeasureMakeBoxInput

# the result types
from .ViewMeasure import ViewMeasure


# turn a pair of anchors into a box
class ViewMeasureMakeBox(graphene.Mutation):
    """
    Turn the first two anchors of the measure path into the corners of a box
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMeasureMakeBoxInput(required=True)

    # the result is the updated measure state
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Turn the first two anchors of the measure path into the corners of a box
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        measures = store.measureMakeBox(viewport=input.viewport)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
