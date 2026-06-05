# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to toggle the anchor selection in multinode mode
class ViewMeasureAnchorToggleSelectionMultiInput(graphene.InputObjectType):
    """
    The payload to toggle the anchor selection in multinode mode
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the index
    index = graphene.Int(required=False)


# end of file
