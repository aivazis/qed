# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to place a measure handle at a pixel
class ViewMeasureAnchorPlaceInput(graphene.InputObjectType):
    """
    The payload to place a measure handle at a pixel
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the handle
    handle = graphene.Int(required=True)
    # the x
    x = graphene.Int(required=True)
    # the y
    y = graphene.Int(required=True)


# end of file
