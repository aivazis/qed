# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene

# the mutations
from .ConnectArchive import ConnectArchive
from .DisconnectArchive import DisconnectArchive
from .ConnectReader import ConnectReader
from .DisconnectReader import DisconnectReader
from .UpdateRangeController import UpdateRangeController
from .UpdateValueController import UpdateValueController


# the mutation anchor
class Mutation(graphene.ObjectType):
    """
    The resting place for mutations
    """

    # data archive connection management
    connectArchive = ConnectArchive.Field()
    disconnectArchive = DisconnectArchive.Field()
    # data reader connection management
    connectReader = ConnectReader.Field()
    disconnectReader = DisconnectReader.Field()

    # updates to ranged controllers
    updateRangeController = UpdateRangeController.Field()
    updateValueController = UpdateValueController.Field()


# end of file
