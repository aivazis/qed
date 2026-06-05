# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for toggling a coordinate in a view's dataset selection
class ViewCoordinateToggleInput(graphene.InputObjectType):
    """
    The payload for toggling a coordinate value in a view's dataset selection
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the reader whose selection is being adjusted
    reader = graphene.String(required=True)
    # the selector axis
    selector = graphene.String(required=True)
    # the coordinate value to toggle
    value = graphene.String(required=True)


# end of file
