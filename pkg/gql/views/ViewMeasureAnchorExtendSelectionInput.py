# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to extend the anchor selection to a given anchor index
class ViewMeasureAnchorExtendSelectionInput(graphene.InputObjectType):
    """
    The payload to extend the anchor selection to a given anchor index
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the index
    index = graphene.Int(required=False)


# end of file
