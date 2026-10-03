# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewFlowToggleLayerInput import ViewFlowToggleLayerInput

# the result types
from .ViewFlow import ViewFlow


# toggle the flow layer of a view
class ViewFlowToggleLayer(graphene.Mutation):
    """
    Toggle the flow layer of the view of a reader
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewFlowToggleLayerInput(required=True)

    # the result is the updated flow layer
    flow = graphene.Field(ViewFlow)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle the flow layer of the view of a reader
        """
        # get the store
        store = info.context["store"]
        # delegate to the store
        flow = store.toggleFlow(viewport=input.viewport, source=input.reader)
        # form the mutation resolution context
        context = {"flow": flow}
        # and resolve the mutation
        return context


# end of file
