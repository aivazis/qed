# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# my channels
from . import channels


# a NISAR SLC
class SLC(qed.flow.product, family="qed.datasets.nisar.slc", implements=qed.protocols.dataset):
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

    # constants
    # the in-memory data layout of NISAR complex data products
    datatype = qed.libqed.nisar.datatypes.complexFloat


    # interface
    def channel(self, name):
        """
        Get the visualization workflow for the given {channel}
        """
        # look up the channel and return it
        return self.channels[name]


    def profile(self, points):
        """
        Sample my data along the path defined by {points}
        """
        # ask my data manager to build a profile
        profile = qed.libqed.datasets.profile(
            source=self.data, datatype=self.datatype, points=points)
        # and return it
        return profile


    def render(self, channel, zoom, origin, shape):
        """
        Render a tile of the given specification
        """
        # resolve my channel
        channel = self.channel(name=channel)
        # render a tile and return it
        return channel.tile(
            source=self, datatype=self.datatype, zoom=zoom, origin=origin, shape=shape)


    # metamethods
    def __init__(self, data, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the dataset
        self.data = data
        # collect statistics from a sample of my data
        self.stats = self._collectStatistics()

        # go through the default channels of my cell type
        for channel in self.cell.channels:
            # get their factories
            cls = getattr(channels, channel)
            # instantiate a workflow for each one
            pipeline = cls(name=f"{self.pyre_name}.{channel}")
            # autotune it
            pipeline.autotune(stats=self.stats)
            # and register it
            self.channels[pipeline.tag] = pipeline

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
        stats = qed.libqed.datasets.stats(
            source=data, datatype=self.datatype, origin=center, shape=tile)

        # and return them
        return stats


# end of file
