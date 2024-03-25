# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# external
import uuid

# support
import qed
import journal

# my parts
from .Channel import Channel
from .View import View


# the server side of the application store
class Store(qed.shells.command, family="qed.cli.ux"):
    """
    The application state as known to the server
    """

    # read-only access to my contents
    @property
    def archives(self):
        # easy enough
        return self._archives.values()

    @property
    def readers(self):
        # easy enough
        return self._readers.values()

    @property
    def selections(self):
        # easy enough
        return self._selections.values()

    @property
    def datasets(self):
        # easy enough
        return self._datasets.values()

    @property
    def views(self):
        # easy enough
        return self._views

    # interface
    # view management
    def collapseView(self, viewport):
        """
        Remove {view} from the list of active views
        """
        # get my views
        views = self._views
        # pop the indicated one
        view = views.pop(viewport)
        # if the pile of views is now empty
        if not views:
            # use the blank view
            view = self._blank
            # add it to the pile
            views.append(self._blank)
        # all done
        return view

    def splitView(self, viewport):
        """
        Remove {view} from the list of active views
        """
        # get my views
        views = self._views
        # grab the view in {viewport}
        view = views[viewport]
        # make a copy of {viewport}
        views.insert(viewport + 1, view)
        # all done
        return view

    def updateView(self, viewport, reader, dataset, channel):
        """
        Update the view in {viewport}
        """
        # lookup the reader
        reader = self.reader(name=reader) if reader else None
        # look up the dataset
        dataset = self.dataset(name=dataset) if dataset else None
        # if there is a channel
        if channel:
            # ask it for its channel
            channel = dataset.channels[channel]
            # get the name of the channel
            channelName = channel.pyre_name
            # build the view name
            viewName = f"{channelName}.view"
        # if not
        else:
            # and a random name
            viewName = str(uuid.uuid1())
        # build the view
        view = View(name=viewName, reader=reader, dataset=dataset, channel=channel)
        # get my views
        views = self._views
        # replace the one at {viewport}
        views[viewport] = view
        # all done
        return view

    def selectReader(self, viewport: int, name: str):
        """
        Locate a reader by {name} and activate it in {viewport}
        """
        # look up the reader selections
        selection = self.selection(name=name)
        # resolve
        selection.resolve()
        # and install in the view
        self._views[viewport] = selection
        # all done
        return selection

    def toggleChannel(self, viewport: int, reader: str, tag: str):
        """
        Toggle the value of the {coordinate} of {axis} in {viewport}
        """
        # get the view
        view = self._views[viewport]
        # if it's not the correct reader
        if view.reader.pyre_name != reader:
            # get the correct view
            view = self.selectReader(viewport=viewport, name=reader)
            # and activate it
            self._views[viewport] = view

        # get the dataset
        dataset = view.dataset
        # if i don't have on
        if not dataset:
            # we have a bug
            firewall = journal.firewall("qed.us.store")
            # complain
            firewall.line(f"no dataset present in viewport {viewport}")
            firewall.line(f"while attempting to toggle the '{tag}' channel")
            firewall.line(f"of {view.reader}")
            # flush
            firewall.log()
            # and bail, just in case firewalls aren't fatal
            return view
        # get the view channel
        current = view.channel
        # if the view doesn't have a channel or it does and it's not this one
        if not current or current.tag != tag:
            # get the channel from teh dataset
            channel = dataset.channels[tag]
            # replace the channel with this one
            view.channel = channel
        # otherwise
        else:
            # clear the channel selection
            view.channel = None

        # N.B.:
        #   toggling the channel never upsets the dataset solution
        #   so there is no reason to resolve the view

        # all done
        return view

    def toggleCoordinate(self, viewport: int, reader: str, axis: str, coordinate: str):
        """
        Toggle the value of the {coordinate} of {axis} in {viewport}
        """
        # get the view
        view = self._views[viewport]
        # if it's not the correct reader
        if view.reader != reader:
            # get the correct view
            view = self.selectReader(viewport=viewport, name=reader)
            # and activate it
            self._views[viewport] = view
        # get the current value of the axis
        current = view.selections.get(axis)
        # if the value is trivial or something else
        if not current or current != coordinate:
            # set {coordinate} as the value
            view.selections[axis] = coordinate
        # otherwise
        else:
            # clear it
            del view.selections[axis]
        # resolve the view
        view.resolve()
        # all done
        return view

    # count
    def archiveCount(self):
        """
        Get the number of connected archives
        """
        # easy enough
        return len(self._archives)

    # searches
    def archive(self, uri):
        """
        Look up an archive by its {uri}
        """
        # easy enough
        return self._archives.get(uri)

    def reader(self, name):
        """
        Look up a reader by its {name}
        """
        # easy enough
        return self._readers.get(name)

    def selection(self, name):
        """
        Look up the selections of a reader by its {name}
        """
        # easy enough
        return self._selections.get(name)

    def dataset(self, name):
        """
        Look up the dataset by name
        """
        # easy enough
        return self._datasets.get(name)

    def channel(self, name):
        """
        Look up the channel view by name
        """
        # easy enough
        return self._channels.get(name)

    # connections
    def connectArchive(self, archive):
        """
        Register {archive}
        """
        # add it to the pile
        self._archives[str(archive.uri)] = archive
        # all done
        return archive

    def connectReader(self, reader):
        """
        Register the {reader}
        """
        # add it to the pile of readers
        self._readers[reader.pyre_name] = reader
        # make a selection for it
        self._selections[reader.pyre_name] = View(
            name=f"{reader.pyre_name}.selections", reader=reader
        )
        # go through its datasets
        for dataset in reader.datasets:
            # and connect them to the store
            self.connectDataset(dataset=dataset)
        # all done
        return reader

    def connectDataset(self, dataset):
        """
        Register the {dataset}
        """
        # add it to the pile
        self._datasets[dataset.pyre_name] = dataset
        # go through its channels
        for channel in dataset.channels.values():
            # and connect them to the store
            self.connectChannel(channel=channel)
        # all done
        return dataset

    def connectChannel(self, channel):
        """
        Register the {channel}
        """
        # get the name of the channel
        channelName = channel.pyre_name
        # build the name of the view
        viewName = f"{channelName}.config"
        # construct the view
        view = Channel(name=viewName, channel=channel)
        # add it to my map
        self._channels[channelName] = view
        # all done
        return channel

    # deletions
    def disconnectArchive(self, uri):
        """
        Remove the archive from the store
        """
        # attempt to
        try:
            # remove the archive
            del self._archives[uri]
        # if it's not there
        except KeyError:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to disconnect '{uri}")
            channel.line(f"the URI does not correspond to a connected data archive")
            # flush
            channel.log()
        # all done
        return

    def disconnectReader(self, name):
        """
        Remove the archive from the store
        """
        # get the reader
        reader = self.reader(name=name)
        # if it's not there
        if not reader:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to remove '{name}")
            channel.line(f"the name does not correspond to a connected product reader")
            # flush
            channel.log()
            # and bail, in case firewalls aren't fatal
            return
        # go through its datasets
        for dataset in reader.datasets:
            # and disconnect them
            self.disconnectDataset(name=dataset.pyre_name)
        # now, remove it from the store
        del self._readers[name]
        # and
        try:
            # its selections
            del self._selections[name]
        # if it's not there
        except KeyError:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to the selections for '{name}")
            channel.line(f"the name does not correspond to a connected product reader")
            # flush
            channel.log()
            # and bail, just in case firewalls aren't fatal
            return reader
        # all done
        return reader

    def disconnectDataset(self, name):
        """
        Remove the archive from the store
        """
        # get the dataset
        dataset = self.dataset(name)
        # if it's not there
        if not dataset:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to disconnect the dataset '{name}")
            channel.line(f"the name does not correspond to a registered dataset")
            # flush
            channel.log()
            # and bail
            return
        # go through its channels
        for channel in dataset.channels.values():
            # and disconnect them
            self.disconnectChannel(name=channel.pyre_name)
        # remove it from the registry
        del self._datasets[name]
        # all done
        return dataset

    def disconnectChannel(self, name):
        """
        Remove the channel from the store
        """
        # look it up
        channel = self.channel(name=name)
        # if it's not there
        if not channel:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to disconnect the channel f'{name}")
            channel.line(f"the name does not correspond to a known dataset channel")
            # flush
            channel.log()
            # and bail, just in case firewalls aren't fatal
            return
        # remove it form the registry
        del self._channels[name]
        # all done
        return channel

    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, spec="store", **kwds)
        # save the root of the document
        self._docroot = docroot
        # map: archive uris -> archives
        self._archives = {}
        # map: reader names -> readers
        self._readers = {}
        # map: reader names -> dataset/channel selection
        self._selections = {}
        # map: dataset name -> dataset
        self._datasets = {}
        # map: channel names -> channels
        self._channels = {}
        # make a trivial view
        self._blank = View(name=f"{self.pyre_name}.blank")
        # initialize my views, a list of {channel} instances that are currently on display
        self._views = [self._blank]
        # now, load the readers that {plexus} harvested from the configuration files
        self.loadPersistentReaders(plexus=plexus)
        # all done
        return

    # implementation details
    # initialization from the plexus configuration
    def loadPersistentReaders(self, plexus):
        """
        Transfer information from the plexus
        """
        # go through the registered archives
        for archive in plexus.archives:
            # and connect them to the store
            self.connectArchive(archive=archive)
        # go through the registered readers
        for reader in plexus.datasets:
            # and connect them to the store
            self.connectReader(reader=reader)
        # clear out the plexus state
        plexus.archives = []
        plexus.datasets = []
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
        channel.line("static assets:")
        channel.indent()
        channel.report(self._docroot.dump())
        channel.outdent()

        # my archives
        channel.line("archives:")
        channel.indent()
        channel.report(self._archives.keys())
        channel.outdent()

        # my readers
        channel.line("readers:")
        channel.indent()
        channel.report(reader.uri for reader in self._readers.values())
        channel.outdent()

        # my datasets
        channel.line("datasets:")
        channel.indent()
        # go through the datasets
        for dataset in self._datasets.values():
            channel.line(f"{dataset}")
            channel.indent()
            channel.line(f"uri: {dataset.uri}")
            # go through the channels
            for chn in dataset.channels.values():
                # sign on
                channel.line(f"channel: {chn}")
                # go through the controllers
                channel.line(f"controllers:")
                for controller, trait in chn.controllers():
                    channel.indent()
                    channel.line(f"controller: {controller}")
                    channel.indent()
                    channel.report(controller.pyre_dump())
                    channel.outdent()
                    channel.outdent()
                # get the view
                view = self._channels[chn.pyre_name]
                # show me the view state
                channel.line(f"view: {view}")
                channel.indent()
                channel.line(f"measure: {view.measure}")
                channel.indent()
                channel.line(f"active: {view.measure.active}")
                channel.line(f"path: {view.measure.path}")
                channel.line(f"closed: {view.measure.closed}")
                channel.line(f"selection: {view.measure.selection}")
                channel.outdent()
                channel.line(f"sync: {view.sync}")
                channel.indent()
                channel.line(f"channel: {view.sync.channel}")
                channel.line(f"zoom: {view.sync.zoom}")
                channel.line(f"scroll: {view.sync.scroll}")
                channel.line(f"path: {view.sync.path}")
                channel.line(f"offsets: {view.sync.offsets}")
                channel.outdent()
                channel.line(f"zoom: {view.zoom}")
                channel.indent()
                channel.line(f"coupled: {view.zoom.coupled}")
                channel.line(f"horizontal: {view.zoom.horizontal}")
                channel.line(f"vertical: {view.zoom.vertical}")
                channel.outdent()
                channel.outdent()
            channel.outdent()
        channel.outdent()

        # flush
        channel.outdent()
        channel.log()


# end of file
