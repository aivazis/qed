# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene


# the payload for an update to the range of a controller
class RangeControllerInput(graphene.InputObjectType):
    """
    The payload for a ranged controller update
    """


    # the fields
    dataset = graphene.ID()
    channel = graphene.ID()

    slot = graphene.String(required=True)

    low = graphene.Float(required=True)
    high = graphene.Float(required=True)


# end of file
