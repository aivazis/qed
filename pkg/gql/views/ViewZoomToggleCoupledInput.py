# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for toggling whether the zoom axes are coupled
class ViewZoomToggleCoupledInput(graphene.InputObjectType):
    """
    The payload to toggle whether horizontal and vertical zoom are coupled
    """

    # the viewport
    viewport = graphene.Int(required=True)


# end of file
