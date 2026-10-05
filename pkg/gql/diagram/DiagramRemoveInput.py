# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to remove a factory from the pipeline diagram
class DiagramRemoveInput(graphene.InputObjectType):
    """
    The payload to remove a factory from the pipeline diagram
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the id of the factory
    node = graphene.ID(required=True)


# end of file
