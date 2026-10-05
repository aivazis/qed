# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .ViewDiagramMoveInput import ViewDiagramMoveInput

# the diagram
from ..diagram.FlowDiagram import FlowDiagram


# move a node of the pipeline diagram
class ViewDiagramMove(graphene.Mutation):
    """
    Move a factory or a slot of the pipeline diagram of a viewport
    """

    # inputs
    class Arguments:
        # the payload
        input = ViewDiagramMoveInput(required=True)

    # the result is the whole diagram, since dropping a slot on another merges the two
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Move {input.node} of the diagram of {input.viewport} to {input.x, input.y, input.z}
        """
        # get the store
        store = info.context["store"]
        # ask it to make the move
        diagram = store.diagramMove(
            viewport=input.viewport, node=input.node, position=(input.x, input.y, input.z)
        )
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
