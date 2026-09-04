# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for resizing a value controller
class ViewValueResizeInput(graphene.InputObjectType):
    """
    The payload to set the display bounds of a value controller by hand
    """

    # the viewport
    viewport = graphene.Int()
    # the channel that owns the controller
    channel = graphene.String()
    # the controller name
    controller = graphene.String(required=True)
    # the new display bounds
    min = graphene.Float(required=True)
    max = graphene.Float(required=True)


# end of file
