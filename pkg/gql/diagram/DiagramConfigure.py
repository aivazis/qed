# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramConfigureInput import DiagramConfigureInput

# the diagram
from .FlowDiagram import FlowDiagram


# change a setting of a factory of the pipeline diagram
class DiagramConfigure(graphene.Mutation):
    """
    Change a setting of a factory of a pipeline diagram, making an instance of its class if it
    has none yet
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramConfigureInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)
    # and why the change was refused, if it was
    error = graphene.String()

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Change a setting of a factory of a pipeline diagram
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        diagram, error = store.diagramConfigure(
            diagram=input.diagram,
            node=input.node,
            trait=input.trait,
            value=input.value,
            name=input.name,
        )
        # and hand off the diagram, along with the reason for a refusal
        return {"diagram": diagram, "error": error}


# end of file
