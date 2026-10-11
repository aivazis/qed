# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to pin a factory of the pipeline diagram in place
class DiagramPinInput(graphene.InputObjectType):
    """
    The payload to pin a factory of the pipeline diagram to a class, or back to its protocol
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the id of the factory
    node = graphene.ID(required=True)
    # the family of the class to pin it to; none pins it back to its protocol
    family = graphene.String()


# end of file
