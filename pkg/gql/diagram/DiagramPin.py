# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramPinInput import DiagramPinInput

# the diagram
from .FlowDiagram import FlowDiagram


# pin a factory of the pipeline diagram in place
class DiagramPin(graphene.Mutation):
    """
    Pin a factory of a pipeline diagram to a class, or back to its protocol
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramPinInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Pin a factory of a pipeline diagram
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        diagram = store.diagramPin(diagram=input.diagram, node=input.node, family=input.family)
        # and hand off the diagram
        return {"diagram": diagram}


# end of file
