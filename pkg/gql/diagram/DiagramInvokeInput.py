# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to invoke a method of a factory of the pipeline diagram
class DiagramInvokeInput(graphene.InputObjectType):
    """
    The payload to invoke a method of the instance a factory of the pipeline diagram is pinned
    to, with no arguments
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the id of the factory
    node = graphene.ID(required=True)
    # the name of the method
    method = graphene.String(required=True)


# end of file
