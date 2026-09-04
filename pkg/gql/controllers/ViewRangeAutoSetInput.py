# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for setting the auto flag of a range controller
class ViewRangeAutoSetInput(graphene.InputObjectType):
    """
    The payload to pin a range controller or release it to follow the data statistics
    """

    # the viewport
    viewport = graphene.Int()
    # the channel that owns the controller
    channel = graphene.String()
    # the controller name
    controller = graphene.String(required=True)
    # the flag
    auto = graphene.Boolean(required=True)


# end of file
