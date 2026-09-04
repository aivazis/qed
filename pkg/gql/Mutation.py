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
from .readers.Stage import Stage

# visualization pipeline controls
from .controllers.ViewRangeReset import ViewRangeReset
from .controllers.ViewValueReset import ViewValueReset
from .controllers.ViewRangeUpdate import ViewRangeUpdate
from .controllers.ViewValueUpdate import ViewValueUpdate
from .controllers.ViewRangeResize import ViewRangeResize
from .controllers.ViewValueResize import ViewValueResize
from .controllers.ViewRangeAutoSet import ViewRangeAutoSet
from .controllers.ViewValueAutoSet import ViewValueAutoSet


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
    viewMeasureToggleLayer = views.viewMeasureToggleLayer.Field()
    # anchor management
    viewMeasureAnchorAdd = views.viewMeasureAnchorAdd.Field()
    viewMeasureAnchorPlace = views.viewMeasureAnchorPlace.Field()
    viewMeasureAnchorMove = views.viewMeasureAnchorMove.Field()
    viewMeasureAnchorRemove = views.viewMeasureAnchorRemove.Field()
    viewMeasureAnchorSplit = views.viewMeasureAnchorSplit.Field()
    viewMeasureAnchorExtendSelection = views.viewMeasureAnchorExtendSelection.Field()
    viewMeasureAnchorToggleSelection = views.viewMeasureAnchorToggleSelection.Field()
    viewMeasureAnchorToggleSelectionMulti = (
        views.viewMeasureAnchorToggleSelectionMulti.Field()
    )
    viewMeasureToggleClosedPath = views.viewMeasureToggleClosedPath.Field()
    viewMeasureReset = views.viewMeasureReset.Field()

    # sync
    viewSyncUpdateOffset = views.viewSyncUpdateOffset.Field()
    viewSyncToggleViewport = views.viewSyncToggleViewport.Field()
    viewSyncToggleAll = views.viewSyncToggleAll.Field()
    viewSyncReset = views.viewSyncReset.Field()

    # look-at center
    viewLookAt = views.viewLookAt.Field()

    # zoom
    viewZoomSetLevel = views.viewZoomSetLevel.Field()
    viewZoomToggleCoupled = views.viewZoomToggleCoupled.Field()
    viewZoomReset = views.viewZoomReset.Field()

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
    # first contact with connected data sources
    stage = Stage.Field()

    # updates to viz controllers
    viewRangeUpdate = ViewRangeUpdate.Field()
    viewValueUpdate = ViewValueUpdate.Field()

    # hand edits of the display bounds of viz controllers
    viewRangeResize = ViewRangeResize.Field()
    viewValueResize = ViewValueResize.Field()

    # pinning and releasing viz controllers
    viewRangeAutoSet = ViewRangeAutoSet.Field()
    viewValueAutoSet = ViewValueAutoSet.Field()

    # resetting of viz controller state
    viewRangeReset = ViewRangeReset.Field()
    viewValueReset = ViewValueReset.Field()


# end of file
