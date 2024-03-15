# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal

# my parts
from .Channel import Channel


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
    def datasets(self):
        # easy enough
        return self._datasets.values()

    # interface
    # count
    def archiveCount(self):
        # easy enough
        return len(self._archives)

    # searches
    def archive(self, uri):
        """
        Look up an archive by its {uri}
        """
        # easy enough
        return self._archives.get(uri)

    def reader(self, uri):
        """
        Look up a reader by its {uri}
        """
        # easy enough
        return self._readers.get(uri)

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
        return

    def connectReader(self, reader):
        """
        Register the {reader}
        """
        # add it to the pile
        self._readers[str(reader.uri)] = reader
        # all done
        return

    def connectDataset(self, dataset):
        """
        Register the {dataset}
        """
        # add it to the pile
        self._datasets[dataset.pyre_name] = dataset
        # go through its channels
        for channel in dataset.channels.values():
            # ge the name of the channel
            channelName = channel.pyre_name
            # build the name of the view
            viewName = f"{channelName}.view"
            # construct the view
            view = Channel(name=viewName, channel=channel)
            # add it to the map
            self._channels[channelName] = view
        # all done
        return

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

    def disconnectReader(self, reader):
        """
        Remove the archive from the store
        """
        # attempt to
        try:
            # remove the reader
            del self._readers[reader]
        # if it's not there
        except KeyError:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to remove '{reader}")
            channel.line(f"the name does not correspond to a connected product reader")
            # flush
            channel.log()
        # all done
        return

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
            channel.line(f"while attempting to remove '{name}")
            channel.line(f"the name does not correspond to a registered dataset")
            # flush
            channel.log()
            # and bail
            return

        # remove it from the registry
        del self._datasets[name]

        # go through its channels
        for channel in dataset.channels.values():
            # ge the name of the channel
            channelName = channel.pyre_name
            # nd remove it form the registry
            del self._channels[channelName]
        # that's all there is to do
        return

    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, spec="store", **kwds)

        # save the root of the document
        self._docroot = docroot
        # build my map of
        self._archives = {
            # uri -> archive
            f"{archive.uri}": archive
            # for all connected archives
            for archive in plexus.archives
        }

        # build a map of normalized uris to readers
        readers = {}
        # by going through the pile in the {plexus}
        for reader in plexus.datasets:
            # get the uri
            uri = reader.uri.clone()
            # normalize the scheme
            if uri.scheme is None:
                # by interpreting its absence as a local file
                uri.scheme = "file"
            # if the reader is managing a local file
            if uri.scheme == "file":
                # convert its address to an absolute path
                uri.address = qed.primitives.path(uri.address).resolve()
            # register this reader
            readers[f"{uri}"] = reader
        # store my map of readers
        self._readers = readers

        # build my map of
        datasets = {
            # name -> dataset state
            f"{dataset.pyre_name}": dataset
            # for all known readers
            for reader in readers.values()
            # for all datasets supported by each reader
            for dataset in reader.datasets
        }
        # store it
        self._datasets = datasets

        # make a map for the dataset chanel viewable state
        channels = {}
        # go through the datasets
        for dataset in datasets.values():
            # and each of their channels
            for channel in dataset.channels.values():
                # ge the name of the channel
                channelName = channel.pyre_name
                # build the name of the view
                viewName = f"{channelName}.view"
                # construct the view
                view = Channel(name=viewName, channel=channel)
                # add it to the map
                channels[channelName] = view
        # store it
        self._channels = channels

        # build my viewports
        self._viewports = {}

        # show me
        # self.pyre_dump()

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
        channel.report(self._readers.keys())
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
                channel.line(f"controllers: {chn}")
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
