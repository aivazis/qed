# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# raw dataset, i.e. a dataset in binary file with no metadata
class Raw(qed.flow.product, family="qed.datasets.raw", implements=qed.protocols.dataset):
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
    cell.default = None
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


    def profile(self, points):
        """
        Sample my data along the path defined by {points}
        """
        # ask my data manager to build a profile
        profile = qed.libqed.datasets.profile(self.data, points)
        # and return it
        return profile


    def render(self, channel, zoom, origin, shape):
        """
        Render a tile of the given specification
        """
        # resolve my channel
        channel = self.channel(name=channel)
        # render a tile and return it
        return channel.tile(source=self, zoom=zoom, origin=origin, shape=shape)


    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # build my data object
        self.data = self._open()
        # get stats on a sample of my data
        self.stats = self._collectStatistics()

        # go through the default channels provided my the data type
        for channel in self.cell.channels:
            # get their factories
            cls = qed.protocols.channel.pyre_resolveSpecification(channel)
            # instantiate a workflow for each one
            pipeline = cls(name=f"{self.pyre_name}.{channel}")
            # autotune it
            pipeline.autotune(stats=self.stats)
            # and register it
            self.channels[channel] = pipeline

        # all done
        return


    # implementation details
    def _open(self):
        """
        Initialize my data source
        """
        # build the name of the buffer factory
        memoryType = f"{self.cell.tag}ConstMap"
        # look up the factory in the {pyre::memory} bindings
        bufferFactory = getattr(qed.libpyre.memory, memoryType)
        # make the memory buffer
        buffer = bufferFactory(str(self.uri))

        # realize the shape
        shape = qed.libpyre.grid.Shape2D(shape=self.shape)
        # build the packing
        packing = qed.libpyre.grid.Canonical2D(shape=shape)
        # grab the grid factory
        gridFactory = getattr(qed.libpyre.grid, f"{memoryType}Grid2D")
        # put it all together
        data = gridFactory(packing, buffer)
        # and return it
        return data


    def _collectStatistics(self):
        """
        Compute statistics on a sample of my data
        """
        # get my data
        data = self.data
        # and my shape
        shape = self.shape

        # make a tile that fits within my shape
        tile = tuple(min(256, s) for s in shape)
        # center it in my shape
        center = tuple((s-t)//2 for s,t in zip(shape, tile))

        # convert to a grid index
        center = qed.libpyre.grid.Index2D(index=center)
        # and a shape
        tile = qed.libpyre.grid.Shape2D(shape=tile)
        # compute the stats
        stats = qed.libqed.datasets.stats(source=data, origin=center, shape=tile)
        # and return them
        return stats


# end of file
