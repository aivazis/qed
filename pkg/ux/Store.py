# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import functools
import pyre
import qed
import journal
import uuid

# support
from .Harvester import Harvester

# my parts
from .Archives import Archives
from .Preparation import Preparation
from .Sample import Sample
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

    # first contact
    def stage(self, name: str | None = None):
        """
        Initiate first contact with the connected data sources, preferring the crew: a
        surveyable source is handed to its team and this call returns at once, leaving the
        event loop free; a non-trivial {name} confines the staging to that source

        Sources whose flavor cannot yet be surveyed, and every source when no fleet has
        been attached, fall back to opening in this process, which blocks
        """
        # assemble the pile of sources this request covers
        pile = self._stagePile(name=name)
        # a name that matched nothing has already been reported
        if pile is None:
            # so there is nothing to do
            return self
        # the ones that cannot travel to a crew
        blocking = []
        # nothing has moved yet
        touched = False
        # go through the pile
        for source in pile:
            # get the standing of this source
            standing = self.lifecycle(name=source.pyre_name)
            # a survey already under way covers this request
            if standing.status == standing.staging:
                # so leave it alone
                continue
            # this source is about to move
            touched = True
            # find out whether this source can be surveyed by a crew
            if self.fleet is None or not getattr(source, "surveyable", False):
                # if not, it opens in this process
                blocking.append(source)
                # on to the next one
                continue
            # otherwise, mark the survey as under way
            standing.begin()
            # and hand the product to its team; the callback receives the discovery
            # record, or the reason the survey failed
            self.fleet.stage(
                reader=source,
                callback=functools.partial(self._surveyed, name=source.pyre_name),
            )
        # the sources that cannot be surveyed open the old way
        for source in blocking:
            # each one in turn, blocking whichever thread runs this
            self._openSource(source=source)
        # if any standing moved
        if touched:
            # let the clients know; a request that found every source already under way
            # changed nothing, so it stays silent rather than costing everyone a refetch
            self._announce()
        # all done
        return self

    def lifecycle(self, name):
        """
        Retrieve the staging record of the source called {name}
        """
        # delegate to my source catalog
        return self._dataSources.lifecycle(name=name)

    def preparation(self, name):
        """
        Retrieve the preparation record of the dataset called {name}
        """
        # a dataset nobody has asked about has not been prepared
        return self._preparations.get(name)

    def prepared(self, dataset) -> bool:
        """
        Report whether {dataset} has everything a view of it wants
        """
        # look up its record
        record = self.preparation(name=dataset.pyre_name)
        # and report whether it has finished
        return record is not None and record.status == record.ready

    def realize(self, dataset):
        """
        Guarantee that {dataset} can supply pixels, opening its product in this process if
        it is a metadata-only twin left behind by a survey

        Rendering never comes through here: tiles are produced by crews that hold their own
        copy of the product. This is the escape hatch for the handful of paths that read
        individual values on the spot -- the pixel peek, the profile -- and it costs one
        real open per product, the first time somebody asks
        """
        # a dataset that already holds a payload needs nothing
        if getattr(dataset, "data", None) is not None:
            # so hand it back
            return dataset
        # find the source that owns it
        source = self._ownerOf(dataset=dataset)
        # a dataset with no owner cannot be rebuilt
        if source is None:
            # so hand it back untouched and let the caller cope
            return dataset
        # get the name of the source
        name = source.pyre_name
        # look for a live copy of the product, opened by an earlier peek
        live = self._realized.get(name)
        # if this is the first ask
        if live is None:
            # carefully, since the product may have become unreachable since the survey
            try:
                # harvest the recipe the same way a survey does
                recipe = qed.nexus.survey(reader=source)
                # resolve the factory
                factory = qed.protocols.reader.pyre_resolveSpecification(
                    spec=recipe.factory
                )
                # build a live instance with file handles of its own; the derived name
                # keeps it clear of the passive source it stands in for
                live = factory(name=f"{name}.local", **recipe.config)
                # and make first contact
                live.open()
            # if anything goes wrong
            except Exception as error:
                # make a channel
                channel = journal.warning("qed.ux.staging")
                # complain
                channel.line(f"could not read values from '{name}'")
                channel.line(f"while opening '{source.uri}' for a direct read")
                channel.line(f"got: {error}")
                # flush
                channel.log()
                # and give up on this product
                return dataset
            # remember it, so the next peek costs nothing
            self._realized[name] = live
        # find the live counterpart of the twin, which is the one with the same identity
        for peer in live.datasets:
            # if this is not it
            if dict(peer.selector) != dict(dataset.selector):
                # keep looking
                continue
            # otherwise, lend the twin the payload and whatever companions it renders with
            dataset.data = peer.data
            # aggregates read through a mask, and packed products through a lookup table
            for companion in ("mask", "bfpq"):
                # if the live dataset carries one
                if getattr(peer, companion, None) is not None:
                    # lend it too
                    setattr(dataset, companion, getattr(peer, companion))
            # the twin can now supply pixels
            return dataset
        # not finding a counterpart means the product changed under us
        channel = journal.warning("qed.ux.staging")
        # complain
        channel.line(f"could not read values from '{dataset.pyre_name}'")
        channel.line(f"the product no longer holds a dataset with its identity")
        # flush
        channel.log()
        # hand it back untouched
        return dataset

    def open(self, name: str | None = None):
        """
        Initiate first contact with the connected data sources in this process, which
        blocks; a non-trivial {name} confines the contact to that source

        This is the fallback for flavors whose products cannot yet travel to a crew, and
        the path the non-serving shells take; {stage} is what the server uses
        """
        # assemble the pile of sources this request covers
        pile = self._stagePile(name=name)
        # a name that matched nothing has already been reported
        if pile is None:
            # so there is nothing to do
            return self
        # go through the pile
        for source in pile:
            # and establish first contact with each one in turn
            self._openSource(source=source)
        # all done
        return self

    # statistics
    def accumulate(self, task, record):
        """
        Fold the statistical {record} of a tile rendered for {task} into the running
        whole-dataset statistics of the task's dataset
        """
        # get the name of the dataset the tile belongs to
        name = getattr(task, "dataset", None)
        # tasks from before the statistics era don't carry one
        if name is None or record is None:
            # and contribute nothing
            return
        # look up the accumulator of the dataset, creating it on first contact
        sample = self._statistics.setdefault(name, Sample())
        # fold in the record
        sample.merge(record=record)
        # make a channel
        channel = journal.debug("qed.ux.stats")
        # and show me the running state
        channel.log(f"{name}: {sample}")
        # reconcile the controllers of the dataset with the accumulated range
        touched = self._reconcile(name=name, sample=sample)
        # if any bounds moved and someone is listening
        if touched and self.notifier is not None:
            # let every live client know so it refetches its state; the notification is
            # coalesced, so a burst of adjustments collapses into a single refetch
            self.notifier()
        # all done
        return

    def statistics(self, name):
        """
        Retrieve the accumulated statistics of the dataset called {name}, if any
        """
        # look it up
        return self._statistics.get(name)

    def _reconcile(self, name, sample):
        """
        Widen the controller bounds of the dataset called {name} to accommodate the
        accumulated {sample}: the slider ranges stretch, but the user's picks are never
        touched, and the session token never rolls, since the rendered pixels are unchanged
        """
        # find the dataset
        dataset = self.dataset(name=name)
        # it may have been disconnected while its tiles were in flight
        if dataset is None:
            # in which case there is nothing to adjust
            return False
        # reduce the sample to the triple the controllers understand
        stats = (sample.min, sample.mean, sample.max)
        # nothing has moved yet
        touched = False
        # go through the reference pipelines of the dataset
        for channel in dataset.channels.values():
            # and their controllers
            for controller, _ in channel.controllers():
                # giving each one a chance to stretch
                touched = controller.widen(stats=stats) or touched
        # the per-view clones mirror the reference configuration, so they stretch too
        for port in self._viewports:
            # one viewport at a time
            touched = port.view().widen(dataset=name, stats=stats) or touched
        # report whether anything moved
        return touched

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
    def view(self, viewport):
        """
        Retrieve the view configuration of {viewport}
        """
        # get the port
        port = self._viewports[viewport]
        # and ask it for its view
        return port.view()

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
            # make a new one
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
        return self._ensurePrepared(view=port.selectSource(source=source))

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
        return self._ensurePrepared(
            view=port.toggleCoordinate(source=source, axis=axis, coordinate=coordinate)
        )

    def setMembers(self, viewport, source, members):
        """
        Set the per-member participation mask of the stack {source} for {viewport}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        return port.setMembers(source=source, members=members)

    def resetMembers(self, viewport, source):
        """
        Restore the stack {source} to its default participation mask for {viewport}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        return port.resetMembers(source=source)

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
        # go through all viewports that are path synced, so a reset honors the sync the
        # same way every other measure mutation does and never leaves peers out of step
        for port in self._syncedWith(viewport=viewport, aspect="path"):
            # reset the measure layer
            view = port.measureReset()
            # an empty viewport has nothing to reset
            if view is None:
                continue
            # hand off the measure configuration
            yield view.measure
        # all done
        return

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

    def vizResizeController(self, viewport, **kwds):
        """
        Set the display bounds of a viz pipeline controller by hand
        """
        # get the {viewport} configuration
        port = self._viewports[viewport]
        # and delegate
        return port.vizResizeController(**kwds)

    def vizSetControllerAuto(self, viewport, auto, **kwds):
        """
        Set the {auto} flag of a viz pipeline controller; a released controller catches up
        with whatever statistics have accumulated for its dataset
        """
        # get the {viewport} configuration
        port = self._viewports[viewport]
        # look up the accumulated statistics of the dataset on display
        sample = self.statistics(name=port.view().dataset.pyre_name)
        # reduce them to the triple the controllers understand, if there are any
        stats = None if sample is None else (sample.min, sample.mean, sample.max)
        # and delegate
        return port.vizSetControllerAuto(auto=auto, stats=stats, **kwds)

    def lookAt(self, viewport, row, col):
        """
        Set the source pixel at the center of {viewport}
        """
        # get the viewport configuration; the look-at is per-viewport, so unlike scroll-sync
        # across a user's own viewports (handled client side) nothing else is touched here
        port = self._viewports[viewport]
        # set the center
        view = port.lookAt(row=row, col=col)
        # hand off the center
        return view.center

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

    # private data
    # the change broadcaster, wired by whoever owns the client connections; when set, it is
    # invoked after controller bounds move so live clients refetch their state
    notifier = None
    # the manager of the crews, wired by whoever assembles them; when set, first contact
    # happens on a worker instead of in this process
    fleet = None
    # the place derived data goes, wired by whoever owns it; the crews are told where it is,
    # so the levels they build land where this process will look for them
    workspace = None

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
        # the whole-dataset statistics accumulators, keyed by dataset name, populated as
        # rendered tiles report their samples
        self._statistics = {}
        # the live copies of surveyed products, keyed by source name, opened on demand by
        # the handful of paths that read individual values in this process
        self._realized = {}
        # what has been done to make each dataset worth looking at, keyed by dataset name
        self._preparations = {}
        # the pyramid builds behind them, keyed the same way, while they are under way
        self._builds = {}

        # all done
        return

    # implementation details
    # staging
    def _ownerOf(self, dataset):
        """
        Find the source that owns {dataset}
        """
        # go through my sources
        for source in self.sources:
            # looking for the one that lists this dataset
            if any(candidate is dataset for candidate in source.datasets):
                # hand it off
                return source
        # not finding one leaves the dataset orphaned
        return None

    def _stagePile(self, name):
        """
        Assemble the sequence of sources a staging request covers
        """
        # with no name, the request covers a snapshot of every registered source
        if name is None:
            # so hand them all off
            return list(self.sources)
        # otherwise, look up the one that was named
        source = self.source(name=name)
        # if there is such a source
        if source is not None:
            # the request covers it alone
            return [source]
        # a name that matches nothing is a bug in whoever built the request
        channel = journal.warning("qed.ux.staging")
        # complain
        channel.line(f"could not stage '{name}'")
        channel.line(f"there is no such source")
        # flush
        channel.log()
        # and report that there is nothing to do
        return None

    def _openSource(self, source):
        """
        Establish first contact with {source} in this process
        """
        # get its standing
        standing = self.lifecycle(name=source.pyre_name)
        # first contact is under way
        standing.begin()
        # carefully, since the product may be unreachable or malformed
        try:
            # establish first contact
            source.open()
        # if anything goes wrong
        except Exception as error:
            # make a channel
            channel = journal.warning("qed.cli")
            # complain
            channel.line(f"could not open '{source.pyre_name}'")
            channel.line(f"while establishing first contact with '{source.uri}'")
            channel.line(f"got: {error}")
            # flush
            channel.log()
            # record the failure, retaining the reason; the source stays listed, so the
            # client can show what went wrong and offer a retry
            standing.fail(error=error)
            # and hand it back
            return source
        # re-register the survivor, so the dataset index reflects what it discovered
        self.connectSource(source=source)
        # the source is viewable
        standing.succeed()
        # let the views catch up with what it found
        self._refreshViewports()
        # all done
        return source

    def _surveyed(self, name, result=None, error=None):
        """
        Take delivery of the outcome of the survey of the source called {name}
        """
        # get its standing
        standing = self.lifecycle(name=name)
        # look up the source; it may have been disconnected while the survey ran
        source = self.source(name=name)
        # if it is gone
        if source is None:
            # its report has nowhere to land
            return self
        # if the survey failed
        if error is not None:
            # make a channel
            channel = journal.warning("qed.ux.staging")
            # complain
            channel.line(f"could not stage '{name}'")
            channel.line(f"while surveying '{source.uri}'")
            channel.line(f"got: {error}")
            # flush
            channel.log()
            # record the failure, retaining the reason for the client to display
            standing.fail(error=error)
        # otherwise
        else:
            # hydrate the passive reader from what the survey found; nothing in this
            # process touches the product
            result.hydrate(reader=source)
            # re-register it, so the dataset index reflects what the survey discovered
            self.connectSource(source=source)
            # the source is viewable
            standing.succeed()
            # let the views catch up with what it found
            self._refreshViewports()
        # either way, the standing moved, so let the clients know
        self._announce()
        # all done
        return self

    def _ensurePrepared(self, view):
        """
        Make sure the dataset {view} has landed on is being made worth looking at
        """
        # a view without a dataset has nothing to prepare
        dataset = getattr(view, "dataset", None)
        # so leave it alone
        if dataset is None:
            # and hand the view back untouched
            return view
        # the name that keys its record
        name = dataset.pyre_name
        # a dataset somebody already asked about is already being seen to
        if name in self._preparations:
            # so there is nothing to start
            return view
        # a product that cannot travel to a crew cannot be prepared by one either, and
        # without a fleet there is nobody to do the work
        source = view.reader
        # so check both
        if self.fleet is None or not getattr(source, "surveyable", False):
            # and leave the view as it has always been: rendered straight off the product
            return view
        # open a record and mark the work as under way
        record = Preparation()
        # remember it before dispatching, so a second request finds it
        self._preparations[name] = record
        # the rasters the dataset is read alongside get their levels too, since a masked
        # render reads all of them at one depth or none of them
        rasters = [dataset] + list(dataset.companions().values())
        # the builds, one per raster
        builds = []
        # go through them
        for raster in rasters:
            # the pyramid, laid over a dataset this process never reads
            pyramid = qed.readers.nisar.pyramid(
                reader=source, dataset=raster, workspace=self.workspace
            )
            # the accumulator its first level folds into, shared with the widen path
            statistics = self._statistics.setdefault(raster.pyre_name, Sample())
            # the build; only the dataset itself reports the seed, since the companions
            # have nothing to say about when the view is worth looking at
            build = qed.nexus.build(
                reader=source,
                dataset=raster,
                pyramid=pyramid,
                fleet=self.fleet,
                statistics=statistics,
                onProgress=functools.partial(self._progressed, name=raster.pyre_name),
                onSeeded=(
                    functools.partial(self._seeded, name=name)
                    if raster is dataset
                    else None
                ),
                onDone=functools.partial(self._built, name=name),
                onFailed=functools.partial(self._buildFailed, name=name),
            )
            # add it to the pile
            builds.append(build)
        # keep the pile, so completion can be judged over all of them
        self._builds[name] = builds
        # and start them
        for build in builds:
            # each hands out its first level
            build.start()
        # let the clients know there is now something to wait for
        self._announce()
        # hand the view back
        return view

    def _progressed(self, name, build):
        """
        The statistics of the dataset called {name} have moved, since more of its first
        level has reported
        """
        # widen the controller bounds; the picks and the session token stay put
        touched = self._reconcile(name=name, sample=build.statistics)
        # if anything moved, let the clients know
        if touched:
            # by announcing
            self._announce()
        # all done
        return self

    def _seeded(self, name, build):
        """
        The first tiles of the dataset called {name} have reported, so its statistics are
        an estimate rather than a guess
        """
        # get the record
        record = self._preparations.get(name)
        # a preparation nobody is tracking is nobody's business
        if record is None:
            # so leave it alone
            return self
        # mark it
        record.seed()
        # and let the clients know the view is worth looking at
        self._announce()
        # all done
        return self

    def _built(self, name, build):
        """
        One of the builds behind the preparation of the dataset called {name} is complete
        """
        # get the record
        record = self._preparations.get(name)
        # a preparation nobody is tracking is nobody's business
        if record is None:
            # so leave it alone
            return self
        # the preparation is done when every build is
        if all(build.done for build in self._builds.get(name, ())):
            # a build that failed has already marked the record
            if record.status != record.failed:
                # otherwise, the work succeeded
                record.succeed()
            # let go of the builds
            self._builds.pop(name, None)
            # and let the clients know
            self._announce()
        # all done
        return self

    def _buildFailed(self, name, build, error):
        """
        One of the builds behind the preparation of the dataset called {name} failed
        """
        # make a channel
        channel = journal.warning("qed.ux.preparation")
        # complain
        channel.line(f"could not prepare '{name}'")
        channel.line(f"got: {error}")
        # flush
        channel.log()
        # get the record
        record = self._preparations.get(name)
        # a preparation nobody is tracking is nobody's business
        if record is None:
            # so leave it alone
            return self
        # mark it; a failure is not worth waiting for, since the view renders anyway, just
        # less well
        record.fail(error=error)
        # let go of the builds
        self._builds.pop(name, None)
        # and let the clients know
        self._announce()
        # all done
        return self

    def _refreshViewports(self):
        """
        Let every bound view reconcile itself with the datasets its reader now exposes
        """
        # go through the viewports
        for port in self._viewports:
            # get the view
            view = port.view()
            # views without a source have nothing to reconcile
            if view.reader is None:
                # so leave them alone
                continue
            # everybody else was built before first contact and holds no pipelines, so
            # they get to refresh themselves against the discovered datasets
            view.refresh()
        # all done
        return self

    def _announce(self):
        """
        Let every live client know that something it displays has moved
        """
        # if anybody is listening
        if self.notifier is not None:
            # let them know; the notification is coalesced, so a burst of standings
            # moving collapses into a single refetch per client
            self.notifier()
        # all done
        return self

    def _loadPersistentArchives(self, plexus):
        """
        Transfer the persistent data sources and their datasets from the plexus
        """
        # build the map
        archives = Archives()
        # go through the plexus archives, resolving each entry on its own
        for archive in self._drain(plexus=plexus, alias="archives"):
            # and connect the survivors
            archives.addArchive(archive=archive)
        # the store is now the authority on the connected archives; empty the plexus pile,
        # recording the handoff as the provenance
        plexus.pyre_setTrait(
            alias="archives",
            value=[],
            locator=pyre.tracking.simple(
                "while handing the data archives to the store"
            ),
        )
        # all done
        return archives

    def _loadPersistentSources(self, plexus):
        """
        Transfer the persistent data sources and their datasets from the plexus
        """
        # build the map
        sources = Sources()
        # go through the plexus datasets, resolving each entry on its own so a bad one is
        # discarded with a warning instead of taking the application down
        for reader in self._drain(plexus=plexus, alias="datasets"):
            # and connect the survivors
            sources.addSource(source=reader)
        # readers built from bare command line uris arrive as live components on a side
        # pile, since the command line processor must not disturb the configured entries
        for reader in plexus._cliSources or []:
            # connect them alongside the configured ones
            sources.addSource(source=reader)
        # go through the plexus stacks, which present as reader-like sources
        for stack in self._drain(plexus=plexus, alias="stacks"):
            # and connect them as well
            sources.addSource(source=stack)
        # the store is now the authority on the connected sources; empty the plexus piles,
        # recording the handoff as the provenance
        locator = pyre.tracking.simple("while handing the data sources to the store")
        plexus.pyre_setTrait(alias="datasets", value=[], locator=locator)
        plexus.pyre_setTrait(alias="stacks", value=[], locator=locator)
        # all done
        return sources

    def _drain(self, plexus, alias):
        """
        Resolve the entries of the plexus trait bound to {alias} one at a time, so that a
        bad entry is discarded with a warning instead of aborting the boot

        Reading the trait normally converts the whole pile as a unit, and one bad entry
        raises while the application is still being constructed; reading the raw
        configuration instead gives every entry its own chance to resolve
        """
        # find the trait descriptor
        trait = plexus.pyre_trait(alias)
        # its per-entry schema is the facility that resolves specs into components
        schema = trait.schema
        # carefully
        try:
            # locate the slot that holds the trait configuration
            node = plexus.pyre_nameserver.getNode(plexus.pyre_inventory.key[trait.name])
            # save its converter
            saved = node.postprocessor
            # disable it
            node.postprocessor = pyre.schemata.identity().coerce
            # so the read produces the raw configuration
            raw = node.value
            # and restore the converter
            node.postprocessor = saved
        # if the raw configuration is unreachable, e.g. an anonymous plexus
        except Exception:
            # fall back to the normal conversion, preserving the historical behavior
            yield from getattr(plexus, alias)
            # and done
            return

        # normalize the raw value into a pile of entries: a missing setting
        if raw is None:
            # contributes nothing
            entries = []
        # a string carries comma separated specs, possibly wrapped in grouping delimiters
        elif isinstance(raw, str):
            # split it the way the framework does
            entries = [
                entry.strip()
                for entry in raw.strip("[]{}()").split(",")
                if entry.strip()
            ]
        # a sequence is already a pile
        elif isinstance(raw, (list, tuple)):
            # take it as is
            entries = list(raw)
        # anything else
        else:
            # is a single entry
            entries = [raw]

        # go through the entries
        for entry in entries:
            # live components, e.g. the default archives, pass through unharmed
            if hasattr(entry, "pyre_family"):
                # hand it off
                yield entry
                # and move on
                continue
            # everything else is a spec that must be resolved; carefully
            try:
                # exactly the way the framework resolves a single pile entry
                component = schema.process(value=entry, incognito=True)
            # any failure at all
            except Exception as error:
                # make a channel
                channel = journal.warning("qed.cli")
                # complain
                channel.line(f"could not load '{entry}'")
                channel.line(f"while processing the '{alias}' configuration")
                channel.line(f"got: {error}")
                # flush
                channel.log()
                # and discard the entry
                continue
            # a survivor joins the pile
            yield component
        # all done
        return

    def _loadPersistentViewports(self, plexus, sources):
        """
        Transfer the persistent viewports from the plexus
        """
        # make a pile
        viewports = []
        # go through the plexus views, resolving each entry on its own so a bad one is
        # discarded with a warning instead of taking the application down; note that,
        # unlike the source piles, the {views} trait is not emptied afterwards: it is a
        # startup seed that nothing re-reads, and live view state persists through the
        # configuration store rather than the trait
        for view in self._drain(plexus=plexus, alias="views"):
            # carefully, since cloning exercises the view configuration
            try:
                # make a viewport with a clone of each one
                viewport = Viewport(name=str(uuid.uuid1()), view=view.clone())
            # if the view configuration is broken
            except Exception as error:
                # make a channel
                channel = journal.warning("qed.cli")
                # complain
                channel.line(f"could not build a viewport for '{view}'")
                channel.line(f"while processing the 'views' configuration")
                channel.line(f"got: {error}")
                # flush
                channel.log()
                # and discard the entry
                continue
            # add the survivor to the pile
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
