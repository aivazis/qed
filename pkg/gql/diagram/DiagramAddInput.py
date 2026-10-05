# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to place a new factory on the pipeline diagram
class DiagramAddInput(graphene.InputObjectType):
    """
    The payload to place a new factory on the pipeline diagram
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the family of the factory
    family = graphene.String(required=True)
    # where it goes
    x = graphene.Float(required=True)
    y = graphene.Float(required=True)
    z = graphene.Float(required=True)


# end of file
