# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for updating the value of a controller
class ViewValueUpdateInput(graphene.InputObjectType):
    """
    The payload to update the value of a controller
    """

    # the viewport
    viewport = graphene.Int()
    # the channel that owns the controller
    channel = graphene.String()
    # the controller name
    controller = graphene.String(required=True)
    # the value parameters
    min = graphene.Float(required=True)
    value = graphene.Float(required=True)
    max = graphene.Float(required=True)


# end of file
