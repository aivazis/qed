# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramInstantiateInput import DiagramInstantiateInput

# the diagram
from .FlowDiagram import FlowDiagram


# pin a factory of the pipeline diagram to a new instance
class DiagramInstantiate(graphene.Mutation):
    """
    Pin a factory of a pipeline diagram to a new instance of a class
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramInstantiateInput(required=True)

    # the result is the whole diagram
    diagram = graphene.Field(FlowDiagram)
    # and why the change was refused, if it was
    error = graphene.String()

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Pin a factory of a pipeline diagram to a new instance of a class
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        diagram, error = store.diagramInstantiate(
            diagram=input.diagram, node=input.node, family=input.family, name=input.name
        )
        # and hand off the diagram, along with the reason for a refusal
        return {"diagram": diagram, "error": error}


# end of file
