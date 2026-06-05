# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for setting the zoom level
class ViewZoomSetLevelInput(graphene.InputObjectType):
    """
    The payload to set the zoom level
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the horizontal zoom level
    horizontal = graphene.Float(required=True)
    # the vertical zoom level
    vertical = graphene.Float(required=True)


# end of file
