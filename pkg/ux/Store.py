# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
import uuid

# support
from .Harvester import Harvester

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
        Retrieve a reader given its {name}
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

    def channelSet(self, viewport, source, tag):
        """
        Toggle the value of {channel}
        """
        # identify the source
        source = self.source(name=source)
        # get the {viewport}
        port = self._viewports[viewport]
        # select the source
        port.selectSource(source=source)
        # get all the channel synced viewports
        for port in self._syncedWith(viewport=viewport, aspect="channel"):
            # get the view
            view = port.view()
            # get its source
            source = view.reader
            # if this view has no reader
            if not source:
                # skip it
                continue
            # get its dataset
            dataset = view.dataset
            # if this view has no selected dataset
            if not dataset:
                # skip it
                continue
            # if the dataset doesn't understand the tag
            if tag not in dataset.channels:
                # skip it
                continue
            # otherwise, set the channel
            yield view.setChannel(tag=tag)
        # all done
        return

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

    def toggleFlow(self, viewport, source):
        """
        Toggle the measure layer state on {viewport}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # toggle the measure layer
        view = port.toggleFlow(source=source)
        # and return the flow
        return view.flow

    def toggleMeasure(self, viewport, source):
        """
        Toggle the measure layer state on {viewport}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # toggle their measure layer
            view = port.toggleMeasure(source=source)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAddAnchor(self, viewport, x, y, index):
        """
        Add an anchor to the path of the measure layer of the current viewport
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # and add an anchor to their path
            view = port.measureAddAnchor(x=x, y=y, index=index)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorPlace(self, viewport, handle, x, y):
        """
        Place an existing anchor at the specific ({x}, {y}) location
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # place the indicated anchor at the specified location
            view = port.measureAnchorPlace(handle=handle, x=x, y=y)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorMove(self, viewport, handle, dx, dy):
        """
        Displace the current anchor selection of {viewport}
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # move the indicated anchor to a new location
            view = port.measureAnchorMove(handle=handle, dx=dx, dy=dy)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorRemove(self, viewport, anchor):
        """
        Remove an anchor from the pile
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # remove the indicated anchor
            view = port.measureAnchorRemove(anchor=anchor)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorSplit(self, viewport, anchor):
        """
        Split in two the leg that starts at an anchor
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # create a new anchor after the indicated one
            view = port.measureAnchorSplit(anchor=anchor)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorExtendSelection(self, viewport, index):
        """
        Extend the anchor selection of {viewport} to the given {index}
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # extend the selection
            view = port.measureAnchorExtendSelection(index=index)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorToggleSelection(self, viewport, index):
        """
        Toggle {index} in the anchor selection in single node mode
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # and toggle the indicated index in the anchor selection
            view = port.measureAnchorToggleSelection(index=index)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureAnchorToggleSelectionMulti(self, viewport, index):
        """
        Toggle {index} in the anchor selection in multinode mode
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # and toggle the selection in multinode mode
            view = port.measureAnchorToggleSelectionMulti(index=index)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

    def measureToggleClosedPath(self, viewport):
        """
        Toggle the {closed} path flag
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # get the {closed} flag and invert it
        closed = not port.view().measure.closed
        # go through all viewports that are path synced
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # and adjust their flags
            view = port.measureSetClosedPath(closed=closed)
            # hand off the measure configuration
            yield view.measure
        # all done
        return

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
        # return the sync table
        return view.sync

    def syncToggleAll(self, viewport, aspect):
        """
        Toggle the {aspect} flag of all entries in the sync table
        """
        # the active {view} of {viewport} acts as the reference
        ref = self._viewports[viewport].view()
        # get the value from the active {viewport} and flip it
        value = not getattr(ref.sync, aspect)
        # go through all my viewports
        for port in self._viewports:
            # and ask each one to set its {aspect} flag to the reference value
            port.syncSetAspect(aspect=aspect, value=value)
        # if the flag is now off, there are no possible state changes
        if not value:
            # hand off the updated views from all my viewports
            yield from (port.view() for port in self._viewports)
            # and that's all
            return
        # if the target {aspect} is "scroll", there are no possible state changes
        if aspect == "scroll":
            # hand off the updated views from all my viewports
            yield from (port.view() for port in self._viewports)
            # all done
            return
        # if the target {aspect} is "channel"
        if aspect == "channel":
            # get the reference channel
            channel = ref.channel
            # we'll use its tag, if any, to update all views that support it
            tag = channel.tag if channel else None
            # engage...
            yield from (port.view().setChannel(tag=tag) for port in self._viewports)
            # and done
            return
        # if the aspect is "path"
        if aspect == "path":
            # translate it
            aspect = "measure"
            # and turn the measure layer on
            ref.measure.active = True
        # get the aspect from the reference view
        refAspect = getattr(ref, aspect)
        # go through my viewports
        for port in self._viewports:
            # get its view
            view = port.view()
            # if we have not bumped into the reference view
            if view.pyre_name != ref.pyre_name:
                # get {aspect} from this view
                viewAspect = getattr(view, aspect)
                # mirror the ref state
                self.harvester.configure(component=viewAspect, reference=refAspect)
            # and hand off the updated view
            yield view

        # all done
        return

    def syncToggleViewport(self, viewport, aspect):
        """
        Toggle the {aspect} flag of the sync table entry for {viewport}
        """
        # get the viewport configuration
        port = self._viewports[viewport]
        # get the current value of aspect
        flag = getattr(port.view().sync, aspect)
        # toggle it
        view = port.syncToggleAspect(aspect=aspect)
        # if the flag was on
        if flag:
            # nothing more to do; leaving a sync group does not modify any other state
            return view
        # if {aspect} is {scroll}
        if aspect == "scroll":
            # there is no further state change
            return view
        # if {aspect} is {path}
        if aspect == "path":
            #  activate the measure layer
            view.measure.active = True
        # we may have to sync the state of {viewport} to the group, so get a group representative
        rep = self._syncRep(aspect=aspect)
        # if there isn't one
        if not rep:
            # all done
            return view
        # if {aspect} is {path}
        if aspect == "path":
            # translate
            aspect = "measure"
        # if the target {aspect} is the {channel}
        if aspect == "channel":
            # get the channel of the sync representative
            channel = rep.view().channel
            # and use its tag, if it has one
            return view.setChannel(channel.tag if channel else None)
        # get the {aspect} of view
        viewAspect = getattr(view, aspect)
        # get the aspect of the sync representative
        repAspect = getattr(rep.view(), aspect)
        # copy the {rep} state for {aspect} in {view}
        self.harvester.configure(component=viewAspect, reference=repAspect)
        # all done
        return view

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
        # get its coupled flag and invert it
        flag = not port.view().zoom.coupled
        # now, go through all the synced viewports
        for port in self._syncedWith(viewport=viewport, aspect="zoom"):
            # set the flag
            view = port.zoomSetCoupled(flag=flag)
            # hand the zoom setting off
            yield view.zoom
        # all done
        return

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
        archives = self._loadPersistentArchives(plexus=plexus)
        # map: name -> data source
        sources = self._loadPersistentSources(plexus=plexus)
        # list: the sequence of visible viewports
        viewports = self._loadPersistentViewports(plexus=plexus, sources=sources)

        # record my state
        self._dataArchives = archives
        self._dataSources = sources
        self._viewports = viewports

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

    def _loadPersistentViewports(self, plexus, sources):
        """
        Transfer the persistent viewports from the plexus
        """
        # make a pile
        viewports = []
        # go through the plexus views
        for view in plexus.views:
            # make a viewport with each one
            viewport = Viewport(name=str(uuid.uuid1()), view=view.clone())
            # and add it to the pile
            viewports.append(viewport)
        # if there weren't any
        if not viewports:
            # make a blank one
            viewport = Viewport(name=str(uuid.uuid1()))
            # if there is only one source
            if len(sources) == 1:
                # grab it
                source = tuple(sources.sources())[0]
                # and select it
                viewport.selectSource(source=source)
            # and add it to the pile
            viewports.append(viewport)
        # all done
        return viewports

    def _syncedWith(self, viewport, aspect, exclude=False):
        """
        Build a sequence of viewports that are {aspect} synced with {viewport}
        """
        # get the port
        port = self._viewports[viewport]
        # if {viewport} is not excluded explicitly
        if not exclude:
            # add it to the pile
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

    def _syncRep(self, aspect):
        """
        Find a viewport that is {aspect} synced to act as the class representative
        """
        # go through my viewports
        for index, port in enumerate(self._viewports):
            # get the sync status of {aspect}
            synced = getattr(port.view().sync, aspect)
            # if it's on
            if synced:
                # we have found the representative
                return port
        # if we get this far, there are no {aspect] synced ports
        return None

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

    # the configuration harvester
    harvester = Harvester()


# end of file
