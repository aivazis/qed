# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .ViewDiagramRemoveInput import ViewDiagramRemoveInput

# the diagram
from ..diagram.FlowDiagram import FlowDiagram


# remove a factory from the pipeline diagram
class ViewDiagramRemove(graphene.Mutation):
    """
    Remove a factory from the pipeline diagram of a viewport
    """

    # inputs
    class Arguments:
        # the payload
        input = ViewDiagramRemoveInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Remove a factory from the pipeline diagram of a viewport
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        diagram = store.diagramRemove(viewport=input.viewport, node=input.node)
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
