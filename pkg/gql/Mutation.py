# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene

# the mutations
from .ConnectArchive import ConnectArchive
from .DisconnectArchive import DisconnectArchive
from .UpdateRangeController import UpdateRangeController
from .UpdateValueController import UpdateValueController


# the mutation anchor
class Mutation(graphene.ObjectType):
    """
    The resting place for mutations
    """

    # connect a new data archive
    connectArchive = ConnectArchive.Field()
    # disconnect an existing data archive
    disconnectArchive = DisconnectArchive.Field()

    # updates to ranged controllers
    updateRangeController = UpdateRangeController.Field()
    updateValueController = UpdateValueController.Field()


# end of file
