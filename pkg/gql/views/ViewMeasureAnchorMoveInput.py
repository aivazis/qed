# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to move a measure handle by a pixel delta
class ViewMeasureAnchorMoveInput(graphene.InputObjectType):
    """
    The payload to move a measure handle by a pixel delta
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the handle
    handle = graphene.Int(required=True)
    # the dx
    dx = graphene.Int(required=True)
    # the dy
    dy = graphene.Int(required=True)


# end of file
