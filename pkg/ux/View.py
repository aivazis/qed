# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal


# information about the contents of a view
class View(qed.component, family="qed.views.view", implements=qed.protocols.view):
    """
    Detailed information about the contents of a mounted view
    """

    # state
    reader = qed.protocols.reader()
    reader.default = None
    reader.doc = "the reader whose dataset is being displayed"

    dataset = qed.protocols.dataset()
    dataset.default = None
    dataset.doc = "the displayed dataset"

    channel = qed.protocols.channel()
    channel.default = None
    channel.doc = "the displayed channel"

    selections = qed.properties.kv()
    selections.default = {}
    selections.doc = "an (axis -> selected value) map with the user selections"

    # interface
    def resolve(self):
        """
        Attempt to resolve the view given the current state of its selections
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
        # if we do have enough selections, there must be a dataset that matches
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
        # get the channel
        channel = self.channel
        # if we were able to find a dataset and we have a channel selection
        if dataset and channel:
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
        # all done
        return self

    # framework hooks
    def pyre_configured(self):
        """
        Validate my configuration
        """
        # get my reader
        reader = self.reader
        # if i don't have one
        if not reader:
            # bail with no errors
            return []
        # get the reader datasets
        datasets = reader.datasets
        # if there is only one
        if len(datasets) == 1:
            # grab it
            dataset, *_ = datasets
            # select it
            self.dataset = dataset
            # if it only has one channel
            if len(dataset.channels) == 1:
                # grab it
                channel, *_ = dataset.channels.values()
                # and select it
                self.channel = channel
        # get my selection
        selections = self.selections
        # so we can prime them
        for axis, coordinates in reader.available.items():
            # if there is only one option for this axis
            if len(coordinates) == 1:
                # get it
                coordinate, *_ = coordinates
                # and select it
                selections[axis] = coordinate
        # report success
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
        return


# end of file
