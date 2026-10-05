# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .ViewDiagramMoveGroupInput import ViewDiagramMoveGroupInput

# the diagram
from ..diagram.FlowDiagram import FlowDiagram


# move a group of nodes of the pipeline diagram
class ViewDiagramMoveGroup(graphene.Mutation):
    """
    Move a group of nodes of the pipeline diagram of a viewport, all or nothing
    """

    # inputs
    class Arguments:
        # the payload
        input = ViewDiagramMoveGroupInput(required=True)

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
            viewport=input.viewport,
            nodes=input.nodes,
            anchor=input.anchor,
            position=(input.x, input.y, input.z),
        )
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
