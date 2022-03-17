# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# external
import csv
import io
import journal
# support
import qed


# a NISAR SLC
class SLC(qed.flow.product, family="qed.nisar.datasets.slc", implements=qed.protocols.dataset):
    """
    A raw dataset
    """


    # public data
    # the source
    uri = qed.properties.path()
    uri.default = None
    uri.doc = "the path to the data source"

    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"

    channels = qed.properties.dict(schema=qed.protocols.channel())
    channels.default = {}
    channels.doc = "the table of channels supported by this dataset"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = 0,0
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    selector = qed.properties.kv()
    selector.default = {}
    selector.doc = "a key/value map that identifies the dataset to its reader"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.default = 512,512
    tile.doc = "the preferred shape of dataset subsets"


    # interface
    def channel(self, name):
        """
        Get the visualization workflow for the given {channel}
        """
        # look up the channel and return it
        return self.channels[name]


    def profile(self, encoding, points):
        """
        Sample my data along the path defined by {points} and return the result
        using {encoding} as the format
        """
        # dispatch
        if encoding == "csv":
            # to my {CSV} handler
            return self._csv(points=points)

        # if i don't understand the encoding, call it a bug
        channel = journal.firewall("qed.datasets.raw")
        # explain
        channel.line(f"unsupported encoding '{encoding}'")
        channel.line(f"while generating a data profile for {self.pyre_name}")
        # and complain
        channel.log()
        # bail, just in case the firewall is not fatal
        return


    def stats(self):
        """
        Compute statistics on a sample of my data
        """
        # i did this at construction time
        return self._stats


    # metamethods
    def __init__(self, data, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the dataset
        self.data = data
        # set my shape
        self.shape = data.shape

        # go through the default channels of my cell type
        for channel in self.cell.channels:
            # get their factories
            cls = qed.protocols.channel.pyre_resolveSpecification(channel)
            # and instantiate a workflow for each one
            self.channels[channel] = cls(name=f"{self.pyre_name}.{channel}")

        # collect statistics from a sample of my data
        self._stats = self._collectStatistics()

        # all done
        return


    # implementation details
    def _collectStatistics(self):
        """
        Collect statistics from a sample of my data
        """
        # get my data
        data = self.data
        # and its shape
        shape = data.shape

        # make a tile that fits within my shape
        tile = tuple(min(256, s) for s in shape)
        # center it in my shape
        center = tuple((s-t)//2 for s,t in zip(shape, tile))

        # convert to a grid index
        center = qed.libpyre.grid.Index2D(index=center)
        # and a shape
        tile = qed.libpyre.grid.Shape2D(shape=tile)
        # compute the stats
        stats = qed.libqed.datasets.stats(source=data, zoom=0, origin=center, shape=tile)

        # and return them
        return stats


    # implementation details
    def _csv(self, points):
        """
        Generate a profile by sampling my data along the path defined by {points} and
        return the results encoded as CSV
        """
        # make a buffer so {csv} has someplace to write into
        buffer = io.StringIO()
        # make a writer
        writer = csv.writer(buffer)

        # my headers
        headers = ("line", "sample") + self.cell.headers
        # write them
        writer.writerow(headers)

        # ask my data manager to build a profile
        for entry in qed.libqed.datasets.profile(self.data, points):
            # and record each {entry}
            writer.writerow(entry)

        # all done
        return buffer.getvalue()


# end of file
