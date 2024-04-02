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


# the record of user choices that lead to a channel selection for a viewport
class View(qed.component, family="qed.ux.views.view", implements=qed.protocols.ux.view):
    """
    The collection of view settings
    """

    # configurable state
    measure = qed.protocols.ux.measure()
    sync = qed.protocols.ux.sync()
    zoom = qed.protocols.ux.zoom()

    # interface
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

    def toggleChannel(self, tag):
        """
        Toggle the value of my {channel}
        """
        # get my dataset
        dataset = self.dataset
        # if i don't have one
        if not dataset:
            # it's a bug
            firewall = journal.firewall("qed.ux.store")
            # complain
            firewall.line(f"cannot toggle the channel using the tag '{tag}'")
            firewall.line(f"no dataset selection for {self.reader}")
            # flush
            firewall.log()
            # and bail, just in case firewalls aren't fatal
            return self
        # get the channel
        current = self.channel
        # if there is one and its tag matches {tag}
        if current and current.tag == tag:
            # clear it
            self.channel = None
        # otherwise
        else:
            # set it
            self.channel = dataset.channel(tag)
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
        return

    def setSync(self, aspect, value):
        """
        Toggle the {aspect} flag of my sync table
        """
        # set the {aspect} flag of my sync table to {value}
        setattr(self.sync, aspect, value)
        # all done
        return self

    def toggleSync(self, aspect):
        """
        Toggle the {aspect} flag of my sync table
        """
        # get the value
        flag = getattr(self.scroll, aspect)
        # flip and set it back
        setattr(self.sync, aspect, not flag)
        # all done
        return self

    def toggleScrollSync(self):
        """
        Toggle the scroll flag of my sync table
        """
        # toggle the scroll flag
        self.sync.scroll ^= True
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
            return
        # get the channel
        channel = self.channel
        # if we were able to find a dataset and we have a channel selection
        if channel:
            # it may be left over from a previous interaction; gingerly
            try:
                # look up the channel of the solution that has the same tag
                candidate = dataset.channel(channel.tag)
            # if the solution doesn't have a channel by this tag
            except KeyError:
                # reset the channel
                self.channel = None
            # if all went well
            else:
                # attach the candidate
                self.channel = candidate
        # if we have a dataset but no channel
        else:
            # get the dataset channels
            channels = dataset.channels
            # if there is only one channel
            if len(channels) == 1:
                # grab it and select it
                self.channel, *_ = channels.values()
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
            channel=self.channel,
            selections=dict(self.selections),
            measure=self.measure.clone(),
            sync=self.sync.clone(),
            zoom=self.zoom.clone(),
        )

    # metamethods
    def __init__(
        self, reader=None, dataset=None, channel=None, selections=None, **kwds
    ):
        # chain up
        super().__init__(**kwds)
        # prime my selections
        self.selections = selections or (reader and dict(reader.selections)) or {}
        # build my state
        self.reader = reader
        self.dataset = dataset
        self.channel = channel

        # resolve my state
        self.resolve()
        # all done
        return

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
        return


# end of file
