# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to split in two the leg that starts at an anchor
class ViewMeasureAnchorSplitInput(graphene.InputObjectType):
    """
    The payload to split in two the leg that starts at an anchor
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the anchor
    anchor = graphene.Int(required=True)


# end of file
