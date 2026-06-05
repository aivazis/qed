# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for resetting a ranged controller
class ViewRangeResetInput(graphene.InputObjectType):
    """
    The payload to reset the value range of a ranged controller
    """

    # the viewport
    viewport = graphene.Int()
    # the channel that owns the controller
    channel = graphene.String()
    # the controller name
    controller = graphene.String()


# end of file
