# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .ViewDiagramAddInput import ViewDiagramAddInput

# the diagram
from ..diagram.FlowDiagram import FlowDiagram


# place a new factory on the pipeline diagram
class ViewDiagramAdd(graphene.Mutation):
    """
    Place a new factory on the pipeline diagram of a viewport
    """

    # inputs
    class Arguments:
        # the payload
        input = ViewDiagramAddInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Place a new factory on the pipeline diagram of a viewport
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        diagram = store.diagramAdd(
            viewport=input.viewport, family=input.family, position=(input.x, input.y, input.z)
        )
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
