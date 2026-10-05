# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramMoveInput import DiagramMoveInput

# the diagram
from .FlowDiagram import FlowDiagram


# move a node of the pipeline diagram
class DiagramMove(graphene.Mutation):
    """
    Move a factory or a slot of a pipeline diagram
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramMoveInput(required=True)

    # the result is the whole diagram, since dropping a slot on another merges the two
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Move {input.node} of the diagram {input.diagram} to {input.x, input.y, input.z}
        """
        # get the store
        store = info.context["store"]
        # ask it to make the move
        diagram = store.diagramMove(
            diagram=input.diagram,
            node=input.node,
            position=(input.x, input.y, input.z),
            settled=input.settled,
        )
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
