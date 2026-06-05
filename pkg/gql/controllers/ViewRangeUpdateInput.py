# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for updating the range of a ranged controller
class ViewRangeUpdateInput(graphene.InputObjectType):
    """
    The payload to update the value range of a ranged controller
    """

    # the viewport
    viewport = graphene.Int()
    # the channel that owns the controller
    channel = graphene.String()
    # the controller name
    controller = graphene.String(required=True)
    # the range parameters
    min = graphene.Float(required=True)
    low = graphene.Float(required=True)
    high = graphene.Float(required=True)
    max = graphene.Float(required=True)


# end of file
