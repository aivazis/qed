# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# get my channels
from .channels import channels as channelRegistry


# raw dataset, i.e. a dataset in binary file with no metadata
class Dataset(qed.flow.product,
              family="qed.datasets.isce2.unw", implements=qed.protocols.dataset):
    """
    A line interleaved unwrapped interferogram
    """


    # public data
    # the source
    uri = qed.properties.path()
    uri.default = None
    uri.doc = "the path to the data source"

    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "real32"
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
        profile = qed.libqed.isce2.unwrapped.profile(self.data, points)
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

        # unpack my reduced shape
        lines, samples = self.shape
        # inject the amplitude/phase index as line interleaved
        self.layout = lines, 2, samples

        # build my data object
        self.data = self._open()

        # get stats on a sample of my data
        self.amplitudeStats = self._collectStatistics(channel=0)
        self.phaseStats = self._collectStatistics(channel=1)

        # build the amplitude channel
        amplitude = qed.isce2.channels.licapAmplitude(name="{self.pyre_name}.amplitude")
        # autotune it
        amplitude.autotune(stats=self.amplitudeStats)
        # and register it
        self.channels[amplitude.tag] = amplitude

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

        # realize the layout
        layout = qed.libpyre.grid.Shape3D(shape=self.layout)
        # build the packing
        packing = qed.libpyre.grid.Canonical3D(shape=layout)
        # grab the grid factory
        gridFactory = getattr(qed.libpyre.grid, f"{memoryType}Grid3D")
        # put it all together
        data = gridFactory(packing, buffer)
        # and return it
        return data


    def _collectStatistics(self, channel):
        """
        Compute statistics on a sample of my data
        """
        # get my data
        data = self.data
        # and my layout
        shape = self.shape

        # make a tile that fits within my shape
        tile = tuple(min(256, s) for s in shape)
        # center it in my shape
        center = tuple((s-t)//2 for s,t in zip(shape, tile))

        # convert to a grid index by injecting the index of the {channel}
        center = qed.libpyre.grid.Index3D(index=(center[0], channel, center[1]))
        # only use {channel} values when computing stats
        tile = qed.libpyre.grid.Shape3D(shape=(tile[0], 1, tile[1]))
        # compute them
        stats = qed.libqed.native.stats(source=data, origin=center, shape=tile)
        # and return them
        return stats


# end of file
