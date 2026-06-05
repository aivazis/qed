# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to remove an anchor from the pile
class ViewMeasureAnchorRemoveInput(graphene.InputObjectType):
    """
    The payload to remove an anchor from the pile
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the anchor
    anchor = graphene.Int(required=True)


# end of file
