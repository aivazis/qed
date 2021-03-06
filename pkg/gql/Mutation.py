# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene

# the mutations
from .UpdateRangeController import UpdateRangeController
from .UpdateValueController import UpdateValueController


# the mutation anchor
class Mutation(graphene.ObjectType):
    """
    The resting place for mutations
    """


    # updates to ranged controllers
    updateRangeController = UpdateRangeController.Field()
    updateValueController = UpdateValueController.Field()


# end of file
