# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the mutations
# view management
from . import views

# explorer
from .archives.ConnectArchive import ConnectArchive
from .archives.ConnectEarthAccessArchive import ConnectEarthAccessArchive
from .archives.DisconnectArchive import DisconnectArchive
from .readers.ConnectReader import ConnectReader
from .readers.DisconnectReader import DisconnectReader

# visualization pipeline controls
from .controllers.ResetRangeController import ResetRangeController
from .controllers.ResetValueController import ResetValueController
from .controllers.UpdateRangeController import UpdateRangeController
from .controllers.UpdateValueController import UpdateValueController


# the mutation anchor
class Mutation(graphene.ObjectType):
    """
    The resting place for mutations
    """

    # view management
    viewReaderSelect = views.viewReaderSelect.Field()
    viewCollapse = views.viewCollapse.Field()
    viewSplit = views.viewSplit.Field()
    viewChannelSet = views.viewChannelSet.Field()
    viewCoordinateToggle = views.viewCoordinateToggle.Field()
    viewPersist = views.viewPersist.Field()

    # measure
    viewMeasureToggleLayer = views.measureToggleLayer.Field()
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
    viewMeasureReset = views.measureReset.Field()

    # sync
    viewSyncUpdateOffset = views.syncUpdateOffset.Field()
    viewSyncToggleViewport = views.syncToggleViewport.Field()
    viewSyncToggleAll = views.syncToggleAll.Field()
    viewSyncReset = views.syncReset.Field()

    # zoom
    viewZoomSetLevel = views.zoomSetLevel.Field()
    viewZoomToggleCoupled = views.zoomToggleCoupled.Field()
    viewZoomReset = views.zoomReset.Field()

    # stack member participation
    viewMembersSet = views.viewMembersSet.Field()
    viewMembersReset = views.viewMembersReset.Field()

    # data archive connection management
    connectArchive = ConnectArchive.Field()
    connectEarthAccessArchive = ConnectEarthAccessArchive.Field()
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
