# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
import uuid

# my parts
from .Archives import Archives
from .Sources import Sources
from .Viewport import Viewport


# the server side of the application store
class Store(qed.shells.command, family="qed.cli.ux"):
    """
    The application state as known to the server
    """

    # interface
    def tile(self, viewport, **kwds):
        """
        Extract a data tile from {viewport}
        """
        # get the port
        port = self._viewports[viewport]
        # and delegate
        return port.tile(**kwds)

    # archives
    @property
    def archives(self):
        """
        Retrieve the sequence of registered archives
        """
        # delegate
        return self._dataArchives.archives()

    def archive(self, uri):
        """
        Retrieve an archive given its {uri}
        """
        # easy enough
        return self._dataArchives.archive(uri=uri)

    def nArchives(self):
        """
        Return the number of connected archives
        """
        # easy enough
        return len(self._dataArchives)

    def connectArchive(self, archive):
        """
        Connect a new archive
        """
        # delegate to my archive store
        return self._dataArchives.addArchive(archive=archive)

    def disconnectArchive(self, uri):
        """
        Disconnect an archive
        """
        # delegate to my archive store
        return self._dataArchives.removeArchive(uri=uri)

    # readers
    @property
    def sources(self):
        """
        Retrieve the sequence of registered readers
        """
        # delegate
        yield from self._dataSources.sources()
        # all done
        return

    def source(self, name):
        """
        Retrieve an reader given its {name}
        """
        # easy enough
        return self._dataSources.source(name=name)

    def nSources(self):
        """
        Return the number of connected readers
        """
        # easy enough
        return len(self._dataSources)

    def connectSource(self, source):
        """
        Connect a new data source
        """
        # delegate to my source store
        return self._dataSources.addSource(source=source)

    def disconnectSource(self, name):
        """
        Disconnect a data source
        """
        # delegate to my source store
        return self._dataSources.removeSource(name=name)

    # datasets
    def dataset(self, name):
        """
        Retrieve a dataset given its {name}
        """
        # delegate to my source catalog
        return self._dataSources.dataset(name=name)

    # views
    @property
    def viewports(self):
        """
        Retrieve the sequence of current views
        """
        # go through my pile of views
        yield from self._viewports
        # all done
        return

    def collapseViewport(self, viewport):
        """
        Collapse the indicated {viewport}
        """
        # get my viewports
        viewports = self._viewports
        # pop the indicated one
        port = viewports.pop(viewport)
        # if the pile of viewports is now empty
        if not viewports:
            # make a new onw
            port = Viewport(name=str(uuid.uuid1()))
            # add it to the pile
            viewports.append(port)
        # all done
        return port.view()

    def splitViewport(self, viewport):
        """
        Split the indicated {viewport}
        """
        # get my viewports
        viewports = self._viewports
        # grab the view in {viewport}
        view = viewports[viewport]
        # make a copy of it
        clone = view.clone()
        # add it to the pile
        viewports.insert(viewport + 1, clone)
        # and return it
        return clone.view()

    def selectSource(self, viewport, name):
        """
        Prepare {viewport} to display the source given its {name}
        """
        # locate the source
        source = self.source(name=name)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and ask it to select the named reader
        return port.selectSource(source=source)

    def toggleChannel(self, viewport, source, tag):
        """
        Toggle the value of {channel}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        return port.toggleChannel(source=source, tag=tag)

    def toggleCoordinate(self, viewport, source, axis, coordinate):
        """
        Toggle the value of {coordinate}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        return port.toggleCoordinate(source=source, axis=axis, coordinate=coordinate)

    def toggleMeasure(self, viewport, source):
        """
        Toggle the measure layer state on {viewport}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        view = port.toggleMeasure(source=source)
        # return the measure configuration
        return view.measure

    def measureAddAnchor(self, viewport, x, y, index):
        """
        Add an anchor to the path of the measure layer of the current viewport
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAddAnchor(x=x, y=y, index=index)
        # all done
        return view.measure

    def measureAnchorPlace(self, viewport, handle, x, y):
        """
        Place an existing anchor at the specific ({x}, {y}) location
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorPlace(handle=handle, x=x, y=y)
        # all done
        return view.measure

    def measureAnchorMove(self, viewport, handle, dx, dy):
        """
        Displace the current anchor selection of {viewport}
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorMove(handle=handle, dx=dx, dy=dy)
        # all done
        return view.measure

    def measureAnchorRemove(self, viewport, anchor):
        """
        Remove an anchor from the pile
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorRemove(anchor=anchor)
        # all done
        return view.measure

    def measureAnchorSplit(self, viewport, anchor):
        """
        Split in two the leg that starts at an anchor
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorSplit(anchor=anchor)
        # all done
        return view.measure

    def measureAnchorExtendSelection(self, viewport, index):
        """
        Extend the anchor selection of {viewport} to the given {index}
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorExtendSelection(index=index)
        # all done
        return view.measure

    def measureAnchorToggleSelection(self, viewport, index):
        """
        Toggle {index} in the anchor selection in single node mode
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorToggleSelection(index=index)
        # all done
        return view.measure

    def measureAnchorToggleSelectionMulti(self, viewport, index):
        """
        Toggle {index} in the anchor selection in multinode mode
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureAnchorToggleSelectionMulti(index=index)
        # all done
        return view.measure

    def measureToggleClosedPath(self, viewport):
        """
        Toggle the {closed} path flag
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureToggleClosedPath()
        # all done
        return view.measure

    def measureReset(self, viewport):
        """
        Reset the state of the {measure} layer
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.measureReset()
        # all done
        return view.measure

    def syncSetAspect(self, viewport, aspect, value):
        """
        Update the sync table offsets
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        view = port.syncSetAspect(aspect=aspect, value=value)
        # return the measure configuration
        return view.sync

    def syncToggleAll(self, viewport, aspect):
        """
        Toggle the {aspect} flag of all entries in the sync table
        """
        # get the value from the {viewport} and flip it
        value = not getattr(self._viewports[viewport].view().sync, aspect)
        # go through all my viewports
        for port in self._viewports:
            # and ask each one to set its {aspect} flag to the reference value
            view = port.syncSetAspect(aspect=aspect, value=value)
            # hand off its scroll table
            yield view.sync
        # all done
        return

    def syncToggleViewport(self, viewport, aspect):
        """
        Toggle the {aspect} flag of the sync table entry for {viewport}
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        view = port.syncToggleAspect(aspect=aspect)
        # return the measure configuration
        return view.sync

    def syncReset(self, viewport):
        """
        Reset the state of the {sync} table
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.syncReset()
        # all done
        return view.sync

    def vizResetController(self, viewport, **kwds):
        """
        Reset the configuration of a viz pipeline controller
        """
        # get the {viewport} configuration
        port = self._viewports[viewport]
        # and delegate
        return port.vizResetController(**kwds)

    def vizUpdateController(self, viewport, **kwds):
        """
        Update the configuration of a viz pipeline controller
        """
        # get the {viewport} configuration
        port = self._viewports[viewport]
        # and delegate
        return port.vizUpdateController(**kwds)

    def zoomSetLevel(self, viewport, horizontal, vertical):
        """
        Set the zoom levels
        """
        # go through all the synced viewports
        for port in self._syncedWith(viewport=viewport, aspect="zoom"):
            # set the zoom level
            view = port.zoomSetLevel(horizontal=horizontal, vertical=vertical)
            # and hand the zoom settings off
            yield view.zoom
        # all done
        return

    def zoomToggleCoupled(self, viewport):
        """
        Toggle the lock flag
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        view = port.zoomToggleCoupled()
        # return the measure configuration
        return view.zoom

    def zoomReset(self, viewport):
        """
        Reset the state of the {zoom} info
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # delegate
        view = port.zoomReset()
        # all done
        return view.zoom

    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, spec="store", **kwds)
        # save the root of the document
        self._docroot = docroot
        # build my registries
        # map: name -> data archive
        archives = self._loadPersistentArchives(plexus)
        # map: name -> data source
        sources = self._loadPersistentSources(plexus)
        # my viewports: start out with one
        viewport = Viewport(name=str(uuid.uuid1()))

        # if there is only one source
        if len(sources) == 1:
            # grab it
            source = tuple(sources.sources())[0]
            # and select it
            viewport.selectSource(source=source)

        # record my state
        self._dataArchives = archives
        self._dataSources = sources
        self._viewports = [viewport]

        # all done
        return

    # implementation details
    def _loadPersistentArchives(self, plexus):
        """
        Transfer the persistent data sources and their datasets from the plexus
        """
        # build the map
        archives = Archives()
        # go through the plexus sources
        for archive in plexus.archives:
            # and connect them
            archives.addArchive(archive=archive)
        # clear out the plexus pile
        plexus.archives = []
        # all done
        return archives

    def _loadPersistentSources(self, plexus):
        """
        Transfer the persistent data sources and their datasets from the plexus
        """
        # build the map
        sources = Sources()
        # go through the plexus sources
        for reader in plexus.datasets:
            # and connect them
            sources.addSource(source=reader)
        # clear out the plexus pile
        plexus.datasets = []
        # all done
        return sources

    def _syncedWith(self, viewport, aspect):
        """
        Build a sequence of viewports that are {aspect} synced with {viewport}
        """
        # get the port
        port = self._viewports[viewport]
        # {viewport} is always in the set
        yield port
        # get the sync status of {aspect}
        synced = getattr(port.view().sync, aspect)
        # if it's {aspect} synced
        if synced:
            # hunt down all the others
            for index, port in enumerate(self._viewports):
                # {viewport} should not be double counted
                if index == viewport:
                    # so skip it
                    continue
                # get the sync status of {aspect}
                synced = getattr(port.view().sync, aspect)
                # if it's on
                if synced:
                    # add this viewport to the pile
                    yield port
        # all done
        return

    # debugging support
    def pyre_dump(self):
        """
        Generate a report with my contents
        """
        # make a channel
        channel = journal.info("qed.ux")
        # sign on
        channel.line("qed store:")
        channel.indent()
        # show me the static assets
        # channel.line("static assets:")
        # channel.indent()
        # channel.report(self._docroot.dump())
        # channel.outdent()

        # my archives
        channel.line("archives:")
        channel.indent()
        channel.report(archive.uri for archive in self._dataArchives.archives())
        channel.outdent()

        # my readers
        channel.line("readers:")
        channel.indent()
        channel.report(reader.uri for reader in self._dataSources.sources())
        channel.outdent()

        # flush
        channel.log()
        # all done
        return


# end of file
