# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .DiagramInvokeInput import DiagramInvokeInput

# the diagram
from .FlowDiagram import FlowDiagram

# the rendering of values
from .FlowFactory import FlowFactory

# the refusal to make a product
from .FlowRefusal import FlowRefusal


# invoke a method of a factory of the pipeline diagram
class DiagramInvoke(graphene.Mutation):
    """
    Invoke a method of the instance a factory of a pipeline diagram is pinned to
    """

    # inputs
    class Arguments:
        # the payload
        input = DiagramInvokeInput(required=True)

    # the result is the whole diagram, since the method may have changed the instance
    diagram = graphene.Field(FlowDiagram)
    # what the method returned, rendered as text
    result = graphene.String()
    # and why the call was refused or failed, if it was
    error = graphene.String()
    # or, when the factory would not make one of its products, which one and why
    refusal = graphene.Field(FlowRefusal)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Invoke a method of a factory of a pipeline diagram
        """
        # get the store
        store = info.context["store"]
        # ask it to make the call
        diagram, result, error, refusal = store.diagramInvoke(
            diagram=input.diagram, node=input.node, method=input.method
        )
        # a list, e.g. the products of a generator, reads as its items
        if isinstance(result, list):
            # each rendered on its own
            text = ", ".join(str(FlowFactory.render(value=item)) for item in result)
        # anything else
        else:
            # is rendered the way a setting is
            text = FlowFactory.render(value=result)
        # hand off the diagram, the result, the reason for a failure, and the refusal, if any
        return {
            "diagram": diagram,
            "result": text,
            "error": error,
            "refusal": None if refusal is None else FlowRefusal(**refusal),
        }


# end of file
