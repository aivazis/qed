# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the mutations
# view management
from . import views

# the pipeline diagrams
from . import diagram

# explorer
from .archives.ConnectArchive import ConnectArchive
from .archives.ConnectEarthAccessArchive import ConnectEarthAccessArchive
from .archives.DisconnectArchive import DisconnectArchive
from .archives.ExpandFolder import ExpandFolder
from .archives.CollapseFolder import CollapseFolder
from .archives.PersistArchive import PersistArchive
from .archives.ReconfigureArchive import ReconfigureArchive
from .archives.ReconfigureEarthAccessArchive import ReconfigureEarthAccessArchive
from .archives.RefreshArchive import RefreshArchive
from .archives.RestoreArchives import RestoreArchives
from .readers.ConnectReader import ConnectReader
from .readers.DisconnectReader import DisconnectReader
from .readers.PersistReader import PersistReader
from .readers.Stage import Stage

# the journal
from .journal import journalChannelSet

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

    # the journal: turn a channel on or off, here and on every worker
    journalChannelSet = journalChannelSet.Field()

    # view management: place a reader in a viewport
    viewReaderSelect = views.viewReaderSelect.Field()
    # remove a view
    viewCollapse = views.viewCollapse.Field()
    # split the current viewport
    viewSplit = views.viewSplit.Field()
    # set the channel a view shows
    viewChannelSet = views.viewChannelSet.Field()
    # pick what draws the tiles of a view
    viewEngineSet = views.viewEngineSet.Field()
    # toggle a coordinate value in the dataset selection of a view
    viewCoordinateToggle = views.viewCoordinateToggle.Field()
    # save the reader configuration of a view
    viewPersist = views.viewPersist.Field()

    # flow: toggle the flow layer of the view of a reader
    viewFlowToggleLayer = views.viewFlowToggleLayer.Field()

    # measure: toggle the participation of a reader in the measure layer
    viewMeasureToggleLayer = views.viewMeasureToggleLayer.Field()
    # anchor management: add an anchor to the measure path
    viewMeasureAnchorAdd = views.viewMeasureAnchorAdd.Field()
    # place a measure handle at a pixel
    viewMeasureAnchorPlace = views.viewMeasureAnchorPlace.Field()
    # move a measure handle by a pixel delta
    viewMeasureAnchorMove = views.viewMeasureAnchorMove.Field()
    # remove an anchor
    viewMeasureAnchorRemove = views.viewMeasureAnchorRemove.Field()
    # split in two the leg that starts at an anchor
    viewMeasureAnchorSplit = views.viewMeasureAnchorSplit.Field()
    # extend the anchor selection to a given anchor
    viewMeasureAnchorExtendSelection = views.viewMeasureAnchorExtendSelection.Field()
    # toggle the anchor selection, one anchor at a time
    viewMeasureAnchorToggleSelection = views.viewMeasureAnchorToggleSelection.Field()
    # toggle the anchor selection, many anchors at a time
    viewMeasureAnchorToggleSelectionMulti = views.viewMeasureAnchorToggleSelectionMulti.Field()
    # turn the first two anchors into the corners of a box
    viewMeasureMakeBox = views.viewMeasureMakeBox.Field()
    # toggle whether the measure path is closed
    viewMeasureToggleClosedPath = views.viewMeasureToggleClosedPath.Field()
    # put the measure state back to its saved value
    viewMeasureReset = views.viewMeasureReset.Field()

    # sync: update the sync scroll offset
    viewSyncUpdateOffset = views.viewSyncUpdateOffset.Field()
    # toggle a sync aspect for one viewport
    viewSyncToggleViewport = views.viewSyncToggleViewport.Field()
    # toggle a sync aspect across all viewports
    viewSyncToggleAll = views.viewSyncToggleAll.Field()
    # put the sync state back to its saved value
    viewSyncReset = views.viewSyncReset.Field()

    # look-at center: set the source pixel at the center of a viewport
    viewLookAt = views.viewLookAt.Field()

    # zoom: set the zoom level
    viewZoomSetLevel = views.viewZoomSetLevel.Field()
    # toggle whether the horizontal and vertical zoom are coupled
    viewZoomToggleCoupled = views.viewZoomToggleCoupled.Field()
    # put the zoom state back to its saved value
    viewZoomReset = views.viewZoomReset.Field()

    # stack member participation: set the members that take part in the aggregate views
    viewMembersSet = views.viewMembersSet.Field()
    # restore the membership the stack was primed with
    viewMembersReset = views.viewMembersReset.Field()

    # pipeline diagrams: place a new factory
    diagramAdd = diagram.diagramAdd.Field()
    # move a factory or a slot
    diagramMove = diagram.diagramMove.Field()
    # move a group of nodes, all or nothing
    diagramMoveGroup = diagram.diagramMoveGroup.Field()
    # remove a factory
    diagramRemove = diagram.diagramRemove.Field()

    # data archive connection management: connect an archive
    connectArchive = ConnectArchive.Field()
    # connect an earth access archive
    connectEarthAccessArchive = ConnectEarthAccessArchive.Field()
    # disconnect an archive
    disconnectArchive = DisconnectArchive.Field()
    # put a folder of an archive on display
    expandFolder = ExpandFolder.Field()
    # take a folder of an archive off display
    collapseFolder = CollapseFolder.Field()
    # save an archive
    persistArchive = PersistArchive.Field()
    # point an archive at a new location, keeping its name
    reconfigureArchive = ReconfigureArchive.Field()
    # replace the query of an earth access archive, keeping its name
    reconfigureEarthAccessArchive = ReconfigureEarthAccessArchive.Field()
    # list every folder of an archive on display again
    refreshArchive = RefreshArchive.Field()
    # list the folders on display that have nothing to show, e.g. the ones a session saved
    restoreArchives = RestoreArchives.Field()
    # data reader connection management: connect a reader
    connectReader = ConnectReader.Field()
    # disconnect a reader
    disconnectReader = DisconnectReader.Field()
    # save a reader
    persistReader = PersistReader.Field()
    # first contact with connected data sources
    stage = Stage.Field()

    # updates to viz controllers: the range ones
    viewRangeUpdate = ViewRangeUpdate.Field()
    # and the value ones
    viewValueUpdate = ViewValueUpdate.Field()

    # hand edits of the display bounds of viz controllers: the range ones
    viewRangeResize = ViewRangeResize.Field()
    # and the value ones
    viewValueResize = ViewValueResize.Field()

    # pinning viz controllers, or releasing them to follow the statistics: the range ones
    viewRangeAutoSet = ViewRangeAutoSet.Field()
    # and the value ones
    viewValueAutoSet = ViewValueAutoSet.Field()

    # resetting of viz controller state: the range ones
    viewRangeReset = ViewRangeReset.Field()
    # and the value ones
    viewValueReset = ViewValueReset.Field()


# end of file
