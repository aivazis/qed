# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the payload for an update to the range of a controller
class RangeControllerUpdateInput(graphene.InputObjectType):
    """
    The payload for a ranged controller update
    """

    # the fields
    viewport = graphene.Int()
    channel = graphene.ID()

    controller = graphene.String(required=True)

    min = graphene.Float(required=True)
    low = graphene.Float(required=True)
    high = graphene.Float(required=True)
    max = graphene.Float(required=True)


# end of file
