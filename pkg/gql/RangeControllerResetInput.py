# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the payload of the reset of the state of a controller
class RangeControllerResetInput(graphene.InputObjectType):
    """
    The payload for a ranged controller reset
    """

    # the fields
    viewport = graphene.Int()
    channel = graphene.String()
    controller = graphene.String()


# end of file
