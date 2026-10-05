# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramAddInput import DiagramAddInput

# the diagram
from .FlowDiagram import FlowDiagram


# place a new factory on the pipeline diagram
class DiagramAdd(graphene.Mutation):
    """
    Place a new factory on a pipeline diagram
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramAddInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Place a new factory on a pipeline diagram
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        diagram = store.diagramAdd(
            diagram=input.diagram, family=input.family, position=(input.x, input.y, input.z)
        )
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
