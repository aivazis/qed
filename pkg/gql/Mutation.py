# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# the mutations
# view management
from . import views

# explorer
from .ConnectArchive import ConnectArchive
from .DisconnectArchive import DisconnectArchive
from .ConnectReader import ConnectReader
from .DisconnectReader import DisconnectReader

# visualization pipeline controls
from .ResetRangeController import ResetRangeController
from .ResetValueController import ResetValueController
from .UpdateRangeController import UpdateRangeController
from .UpdateValueController import UpdateValueController


# the mutation anchor
class Mutation(graphene.ObjectType):
    """
    The resting place for mutations
    """

    # view management
    viewSelectReader = views.selectReader.Field()
    viewCollapse = views.collapse.Field()
    viewSplit = views.split.Field()
    viewToggleChannel = views.toggleChannel.Field()
    viewToggleCoordinate = views.toggleCoordinate.Field()
    viewPersist = views.persist.Field()
    # dataset view state
    viewMeasureToggleLayer = views.measureToggleLayer.Field()
    viewToggleScrollSync = views.toggleScrollSync.Field()
    viewToggleAllSync = views.toggleAllSync.Field()
    # anchor management
    viewMeasureAnchorAdd = views.measureAnchorAdd.Field()
    viewMeasureAnchorPlace = views.measureAnchorPlace.Field()
    viewMeasureAnchorMove = views.measureAnchorMove.Field()
    viewMeasureAnchorRemove = views.measureAnchorRemove.Field()
    viewMeasureAnchorSplit = views.measureAnchorSplit.Field()
    viewMeasureAnchorExtendSelection = views.measureAnchorExtendSelection.Field()
    viewMeasureAnchorToggleSelection = views.measureAnchorToggleSelection.Field()
    viewMeasureAnchorToggleSelectionMulti = (
        views.measureAnchorToggleSelectionMulti.Field()
    )
    viewMeasureToggleClosedPath = views.measureToggleClosedPath.Field()
    viewZoomSetLevel = views.zoomSetLevel.Field()
    viewZoomToggleCoupled = views.zoomToggleCoupled.Field()

    # data archive connection management
    connectArchive = ConnectArchive.Field()
    disconnectArchive = DisconnectArchive.Field()
    # data reader connection management
    connectReader = ConnectReader.Field()
    disconnectReader = DisconnectReader.Field()

    # updates to viz controllers
    updateRangeController = UpdateRangeController.Field()
    updateValueController = UpdateValueController.Field()

    # resetting of viz controller state
    resetRangeController = ResetRangeController.Field()
    resetValueController = ResetValueController.Field()


# end of file
