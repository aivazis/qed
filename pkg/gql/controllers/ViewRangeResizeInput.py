# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for resizing a range controller
class ViewRangeResizeInput(graphene.InputObjectType):
    """
    The payload to set the display bounds of a range controller by hand
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
