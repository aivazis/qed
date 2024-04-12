# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import bisect
import uuid

# support
import qed
import journal
import qed.protocols

# configuration stores
from .Source import Source

# helpers
from .Harvester import Harvester


# the record of user choices that lead to a channel selection for a viewport
class View(qed.component, family="qed.ux.views.view", implements=qed.protocols.ux.view):
    """
    The collection of view settings
    """

    # configurable state
    reader = qed.protocols.reader()
    reader.doc = "my data source"

    dataset = qed.protocols.dataset()
    dataset.doc = "my dataset"

    channel = qed.protocols.channel()
    channel.doc = "my channel"

    selections = qed.properties.kv()
    selections.doc = "a key/value store of the user choices towards a dataset selection"

    measure = qed.protocols.ux.measure()
    measure.doc = "the measure layer indicator"

    sync = qed.protocols.ux.sync()
    sync.doc = "my sync table"

    zoom = qed.protocols.ux.zoom()
    zoom.doc = "the zoom level"

    session = qed.properties.str()
    session.doc = "the session token"

    # interface
    def tile(self, channel, zoom, origin, shape):
        """
        Render a tile of data using the {channel} visualization pipeline
        """
        # form the channel name
        name = f"{self.pyre_name}.{channel}"
        # locate the pipeline
        pipeline = self._pipelines[name]
        # and ask my dataset to render the tile
        return self.dataset.render(
            channel=pipeline, zoom=zoom, origin=origin, shape=shape
        )

    def toggleSelection(self, key, value):
        """
        Toggle the {value} of {key} in my {selections}
        """
        # get my selections
        selections = self.selections
        # get the current value key
        current = selections.get(key)
        # if there is one and it's {value}
        if current and current == value:
            # clear it
            del selections[key]
        # otherwise
        else:
            # set it
            selections[key] = value
        # solve the selection
        self.resolve()
        # all done
        return self

    def setChannel(self, tag):
        """
        Set my channel to the one wih {tag}
        """
        # if the tag is trivial
        if tag is None:
            # clear the channel
            self.channel = None
            # and bail
            return self
        # otherwise, get my dataset
        dataset = self.dataset
        # if i don't have one
        if not dataset:
            # it's a bug
            firewall = journal.firewall("qed.ux.store")
            # complain
            firewall.line(f"cannot ser the channel to '{tag}'")
            firewall.line(f"no dataset selection for {self.reader}")
            # flush
            firewall.log()
            # and bail, just in case firewalls aren't fatal
            return self
        # if the tag is understood
        if tag in dataset.channels:
            # build the channel name
            name = f"{self.pyre_name}.{dataset.pyre_name}.{tag}"
            # look it up and set it
            self.channel = self._pipelines[name]
            # solve the selection
            self.resolve()
        # all done
        return self

    def toggleMeasure(self):
        """
        Toggle the measure layer state
        """
        # toggle the active flag
        self.measure.active ^= True
        # all done
        return self

    def measureAddAnchor(self, x, y, index):
        """
        Add an anchor to my measure path
        """
        # get the set of anchors
        anchors = self.measure.path
        # if there is a specific place to put this anchor
        if index is not None:
            # insert it
            anchors.insert(index, (x, y))
        # otherwise
        else:
            # add it at the end
            anchors.append((x, y))
        # all done
        return self

    def measureAnchorPlace(self, handle, x, y):
        """
        Place an existing anchor at the specific ({x}, {y}) location
        """
        # get the measure record
        measure = self.measure
        # get the set of anchors
        anchors = measure.path
        # and store
        anchors[handle] = (x, y)
        # all done
        return self

    def measureAnchorMove(self, handle, dx, dy):
        """
        Move the current selection by ({dx}, {dy})
        """
        # get the dataset shape; don't forget that it's (lines, samples)
        shape = self.dataset.shape
        # get the measure record
        measure = self.measure
        # get the set of anchors
        anchors = measure.path
        # get the selected anchors
        selection = measure.selection
        # figure out who gets moved
        targets = selection if handle in selection else [handle]
        # go though the selected anchors
        for index in targets:
            # get the anchor position
            x, y = anchors[index]
            # clip and update
            x = min(shape[1], max(0, x + dx))
            y = min(shape[0], max(0, y + dy))
            # and store
            anchors[index] = (x, y)
        # all done
        return self

    def measureAnchorRemove(self, anchor):
        """
        Remove an {anchor} from the pile
        """
        # get the measure record
        measure = self.measure
        # get the set of anchors
        anchors = measure.path
        # get the selected anchors
        selection = measure.selection
        # remove the anchor
        anchors.pop(anchor)
        # adjust the selection:
        # - if the anchor is present in the selection it must be removed
        # - anchor indices greater than anchor must be reduced by one
        # find the insertion point
        spot = bisect.bisect_left(selection, anchor)
        # if it's not at the end of the list
        if spot != len(selection):
            # if {anchor} is present, it must be located at {spot}
            present = selection[spot] == anchor
            # if it's there
            if present:
                # drop it
                selection.pop(spot)
            # all downstream indices
            for idx in range(spot, len(selection)):
                # have to be reduce by one
                selection[idx] -= 1
        # all done
        return self

    def measureAnchorSplit(self, anchor):
        """
        Split in two the leg that starts at {anchor}
        """
        # get the measure record
        measure = self.measure
        # get the set of anchors
        anchors = measure.path
        # get the selected anchors
        selection = measure.selection

        # get the starting point
        tail = anchors[anchor]
        # and the end point
        head = anchors[anchor + 1]
        # interpolate to form the coordinates of the new point
        point = tuple(int((h + t) / 2) for h, t in zip(head, tail))
        # add it to the pile
        anchors.insert(anchor + 1, point)

        # adjust the selection:
        # - if both the anchor and its successor are present in the selection, the new node is
        #   also selected
        # - every index in the selection after index has to be incremented by one
        # find the insertion point
        spot = bisect.bisect_left(selection, anchor)

        # all done
        return self

    def measureAnchorExtendSelection(self, index):
        """
        Extend the anchor selection to the given {index}
        """
        # get the current selection
        current = self.measure.selection
        # assuming the selection is always sorted, find the insertion point for {index}
        spot = bisect.bisect_left(current, index)
        # trim to that point
        extended = current[:spot]
        # deduce the starting value
        start = extended[-1] + 1 if extended else 0
        # extend to {index}
        extended.extend(range(start, index + 1))
        # and store
        self.measure.selection = extended
        # all done
        return self

    def measureAnchorToggleSelection(self, index):
        """
        Toggle {index} in single node mode
        """
        # get the current selection
        current = self.measure.selection
        # if {index} is the only selected node, clear the selection;
        # otherwise, make a selection that includes just {index}
        toggled = [] if current == [index] else [index]
        # and store
        self.measure.selection = toggled
        # all done
        return self

    def measureAnchorToggleSelectionMulti(self, index):
        """
        Toggle {index} in multinode mode
        """
        # multinode toggle:
        # - if selection is empty, make one with index in it
        # - if selection non-empty and contains index, drop index from it
        # - if selection non-empty and does not contain index, add index to it

        # make a copy of the current selection
        toggled = self.measure.selection
        # look for a spot for {index}
        spot = bisect.bisect_left(toggled, index)
        # if its place is at the end of the selection
        if spot == len(toggled):
            # the selection does not contain {index}; append it
            toggled.append(index)
        # if the selection is not empty and contains {index}
        elif toggled[spot] == index:
            # drop it from the selection
            toggled.pop(spot)
        # finally, if the selection is on-empty and it doesn't contain {index}
        else:
            # insert it
            toggled.insert(spot, index)
        # store the new selection
        self.measure.selection = toggled
        # all done
        return self

    def measureSetClosedPath(self, closed):
        """
        Set the {closed} path flag
        """
        # toggle the value of the flag
        self.measure.closed = closed
        # all done
        return self

    def measureReset(self):
        """
        Reset the state of the measure configuration
        """
        # get my reader
        reader = self.reader
        # if i don't have on
        if not reader:
            # nothing more to do
            return
        # get my name
        name = self.pyre_name
        # get the reader name
        sourceName = reader.pyre_name
        # pull its configuration
        config = Source(name=f"{sourceName}.view")
        # clone the persistent state
        self.measure.reset(defaults=config.measure)
        # all done
        return self

    def syncSetAspect(self, aspect, value):
        """
        Toggle the {aspect} flag of my sync table
        """
        # set the {aspect} flag of my sync table to {value}
        setattr(self.sync, aspect, value)
        # all done
        return self

    def syncToggleAspect(self, aspect):
        """
        Toggle the {aspect} flag of my sync table
        """
        # get the value
        flag = getattr(self.sync, aspect)
        # flip and set it back
        setattr(self.sync, aspect, not flag)
        # all done
        return self

    def syncReset(self):
        """
        Reset the state of the sync configuration
        """
        # get my reader
        reader = self.reader
        # if i don't have on
        if not reader:
            # nothing more to do
            return
        # get the reader name
        sourceName = reader.pyre_name
        # pull its configuration
        config = Source(name=f"{sourceName}.view")
        # use it to adjust mine
        self.sync.reset(defaults=config.sync)
        # all done
        return self

    def vizResetController(self, name, channel):
        """
        Reset the state of one of my controllers
        """
        # form the name of the pipeline and look it up
        pipeline = self._pipelines[channel]
        # get the controller
        controller = getattr(pipeline, name)
        # get the reference configuration
        reference = getattr(self.dataset.channel(name=pipeline.tag), name)
        # restore the controller configuration
        self.harvester.configure(component=controller, reference=reference)
        # mark is as clean
        controller.dirty = False
        # grab a new session token
        self.session = uuid.uuid1()
        # all done
        return controller

    def vizUpdateController(self, name, channel, configuration):
        """
        Update the state of one of my controllers
        """
        # form the name of the pipeline and look it up
        pipeline = self._pipelines[channel]
        # get the controller
        controller = getattr(pipeline, name)
        # go through the configuration
        for name, value in configuration.items():
            # and adjust the controller state
            setattr(controller, name, value)
        # grab a new session token
        self.session = uuid.uuid1()
        # all done
        return controller

    def zoomSetLevel(self, horizontal, vertical):
        """
        Set the zoom levels
        """
        # get the zoom
        zoom = self.zoom
        # set
        zoom.horizontal = horizontal
        zoom.vertical = vertical
        # all done
        return self

    def zoomSetCoupled(self, flag):
        """
        Set the zoom lock flag
        """
        # set
        self.zoom.coupled = flag
        # all done
        return self

    def zoomReset(self):
        """
        Reset the state of the zoom configuration
        """
        # get my reader
        reader = self.reader
        # if i don't have on
        if not reader:
            # nothing more to do
            return
        # get my name
        name = self.pyre_name
        # get the reader name
        sourceName = reader.pyre_name
        # pull its configuration
        config = Source(name=f"{sourceName}.view")
        # use it to adjust mine
        self.zoom.reset(defaults=config.zoom)
        # all done
        return self

    # state resolution
    def resolve(self):
        """
        Attempt to identify the {dataset} and {channel} that correspond to my {selections}
        """
        # get my reader
        reader = self.reader
        # if i don't have one
        if not reader:
            # there is no solution
            return self
        # get the reader selectors
        selectors = reader.selectors
        # get my selections
        selections = self.selections
        # if we don't have have enough selections
        if len(selections) != len(selectors):
            # clear the dataset
            self.dataset = None
            # nothing else to do
            return self
        # if we do have enough selections, there must be a dataset that matches;
        # go through them
        for dataset in reader.datasets:
            # if its selectors match my selections
            if dataset.selector == selections:
                # it's the one
                self.dataset = dataset
                # go no further
                break
        # if we didn't find a match
        else:
            # there is no solution
            self.dataset = None
            # it could be a bug, but it's also possible that the reader has no datasets
            # so, if the reader has datasets
            if reader.datasets:
                # it's a bug
                firewall = journal.firewall("qed.ux.store")
                # complain
                firewall.line(f"could not solve for the dataset")
                firewall.line(f"in {self}")
                firewall.line(f"with {reader}")
                firewall.line(f"given the following selections:")
                firewall.indent()
                firewall.report(
                    report=(f"{key}: {value}" for key, value in selections.items())
                )
                firewall.outdent()
                # flush
                firewall.log()
                # and bail, just in case firewalls aren't fatal
                return self
        # if we were not able to identify the dataset
        if not dataset:
            # all done
            return self
        # get the channel
        channel = self.channel
        # if we were able to find a dataset and we have a channel selection
        if channel:
            # it may be left over from a previous interaction; gingerly
            try:
                # let's look up the channel of the solution that has the same tag
                # build its name
                name = f"{self.pyre_name}.{dataset.pyre_name}.{channel.tag}"
                # and look it up
                candidate = self._pipelines[name]
            # if the solution doesn't have a channel by this tag
            except KeyError:
                # reset the channel
                self.channel = None
            # if all went well
            else:
                # install it
                self.channel = candidate
        # if we have a dataset but no channel
        else:
            # get the dataset channels
            channels = dataset.channels
            # if there is only one channel
            if len(channels) == 1:
                # get it
                candidate, *_ = channels.values()
                # build the name by which i know this channel
                name = f"{self.pyre_name}.{dataset.pyre_name}.{candidate.tag}"
                # look it up and install it
                self.channel = self._pipelines[name]

        # all done
        return self

    def clone(self):
        """
        Make a copy of me
        """
        # build a new name
        name = str(uuid.uuid1())
        # easy enough
        return type(self)(
            name=name,
            reader=self.reader,
            dataset=self.dataset,
            channel=self.channel.pyre_family(),
            selections=dict(self.selections),
            measure=self.measure.clone(),
            sync=self.sync.clone(),
            zoom=self.zoom.clone(),
        )

    def pipelines(self):
        """
        Build a pipeline registry with all the channels of all my source datasets
        """
        # get my reader
        reader = self.reader
        # if it's trivial
        if not reader:
            # nothing to do
            return {}
        # otherwise, go through its datasets
        for dataset in reader.datasets:
            # form the namespace
            namespace = f"{self.pyre_name}.{dataset.pyre_name}"
            # build my pipelines
            for pipeline in dataset.pipelines(context=namespace):
                # get the reference configuration
                reference = dataset.channel(name=pipeline.tag)
                # mirror its configuration in my pipeline
                self.harvester.configure(component=pipeline, reference=reference)
                # go through its controllers
                for controller, _ in pipeline.controllers():
                    # and mark each one as clean
                    controller.dirty = False
                # hand off the configured pipeline
                yield pipeline
        # all done
        return

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # build my visualization pipeline registry
        self._pipelines = {
            pipeline.pyre_name: pipeline for pipeline in self.pipelines()
        }
        # resolve my state
        self.resolve()
        # all done
        return

    # framework hooks
    def pyre_configured(self, **kwds):
        """
        Adjust my configuration
        """
        # get my reader
        reader = self.reader
        # if i don't have on
        if not reader:
            # nothing more to do; report no errors
            return []
        # otherwise, get my selections
        selections = self.selections
        # if i don't have any
        if len(selections) == 0:
            # copy my reader's
            selections.update(reader.selections)
        # get my name
        name = self.pyre_name
        # get the reader name
        sourceName = reader.pyre_name
        # pull its configuration
        config = Source(name=f"{sourceName}.view")
        # clone the persistent state
        self.measure = config.measure.clone(name=f"{name}.measure")
        self.sync = config.sync.clone(name=f"{name}.sync")
        self.zoom = config.zoom.clone(name=f"{name}.zoom")
        # make my initial session token
        self.session = uuid.uuid1()
        # all done; report no errors
        return []

    # debugging support
    def pyre_dump(self, channel=None):
        """
        Report my state
        """
        # make a channel
        channel = channel or journal.info("qed.ux.store")
        # sign in
        channel.line(f"{self}")
        # report
        channel.indent()
        channel.line(f"reader: {self.reader}")
        channel.line(f"dataset: {self.dataset}")
        channel.line(f"channel: {self.channel}")
        channel.line(f"dataset selections:")
        channel.indent()
        for key, value in self.selections.items():
            channel.line(f"{key}: {value}")
        channel.outdent()
        channel.outdent()
        # flush
        channel.log()
        # all done
        return self

    # constants
    harvester = Harvester()


# end of file
