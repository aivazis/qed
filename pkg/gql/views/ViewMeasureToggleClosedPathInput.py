# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to toggle whether the measure path is closed
class ViewMeasureToggleClosedPathInput(graphene.InputObjectType):
    """
    The payload to toggle whether the measure path is closed
    """

    # the viewport
    viewport = graphene.Int(required=True)


# end of file
