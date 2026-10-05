# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramMoveGroupInput import DiagramMoveGroupInput

# the diagram
from .FlowDiagram import FlowDiagram


# move a group of nodes of the pipeline diagram
class DiagramMoveGroup(graphene.Mutation):
    """
    Move a group of nodes of a pipeline diagram, all or nothing
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramMoveGroupInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Move {input.nodes} so that {input.anchor} lands at {input.x, input.y, input.z}
        """
        # get the store
        store = info.context["store"]
        # ask it to make the move
        diagram = store.diagramMoveGroup(
            diagram=input.diagram,
            nodes=input.nodes,
            anchor=input.anchor,
            position=(input.x, input.y, input.z),
        )
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
