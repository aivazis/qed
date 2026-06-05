# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to add an anchor to the measure path
class ViewMeasureAnchorAddInput(graphene.InputObjectType):
    """
    The payload to add an anchor to the measure path
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the x
    x = graphene.Int(required=True)
    # the y
    y = graphene.Int(required=True)
    # the index
    index = graphene.Int(required=False)


# end of file
