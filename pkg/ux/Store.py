# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal


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

    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, spec="store", **kwds)

        # make a channel
        channel = journal.debug("qed.ux")
        # sign on
        channel.line("qed store:")
        channel.indent()
        # show me the static assets
        channel.line("static assets:")
        channel.indent()
        channel.report(docroot.dump())
        channel.outdent()

        # build my map of
        self._archives = {
            # uri -> archive
            f"{archive.uri}": archive
            # for all connected archives
            for archive in plexus.archives
        }
        # show me
        channel.line("archives:")
        channel.indent()
        channel.report(self._archives.keys())
        channel.outdent()

        # build a map readers
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
        # and show them to me
        channel.line("readers:")
        channel.indent()
        channel.report(self._readers.keys())
        channel.outdent()

        # build my map of
        self._datasets = {
            # name -> dataset state
            f"{dataset.pyre_name}": dataset
            # for all known readers
            for reader in readers.values()
            # for all datasets supported by each reader
            for dataset in reader.datasets
        }
        # and show them to me
        channel.line("datasets:")
        channel.indent()
        # go through the datasets
        for dataset in self._datasets.values():
            channel.line(f"{dataset}")
            channel.indent()
            channel.line(f"uri: {dataset.uri}")
            # go through the channels
            for chn in dataset.channels.values():
                channel.line(f"channel: {chn}")
                # go through the controllers
                for controller, trait in chn.controllers():
                    channel.indent()
                    channel.line(f"controller: {controller}")
                    channel.indent()
                    channel.report(controller.pyre_dump())
                    channel.outdent()
                    channel.outdent()
            channel.outdent()
        channel.outdent()

        # flush
        channel.outdent()
        channel.log()

        # all done
        return


# end of file
