# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene


# the payload for an update to the range of a controller
class ValueControllerUpdateInput(graphene.InputObjectType):
    """
    The payload for a value controller update
    """

    # the fields
    dataset = graphene.ID()
    channel = graphene.ID()

    slot = graphene.String(required=True)

    value = graphene.Float(required=True)


# end of file
