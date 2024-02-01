# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import journal

# support
import qed

# get my channels
from .channels import channels as channelRegistry


# raw dataset, i.e. a dataset in binary file with no metadata
class Dataset(
    qed.flow.product, family="qed.datasets.isce2.unw", implements=qed.protocols.dataset
):
    """
    A line interleaved unwrapped interferogram
    """

    # public data
    # the source
    uri = qed.properties.uri()
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
    origin.default = 0, 0
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    selector = qed.properties.kv()
    selector.default = {}
    selector.doc = "a key/value map that identifies the dataset to its reader"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.default = 512, 512
    tile.doc = "the preferred shape of dataset subsets"

    # interface
    def channel(self, name):
        """
        Get the visualization workflow for the given {channel}
        """
        # look up the channel and return it
        return self.channels[name]

    def peek(self, pixel):
        """
        Build a family of value representations at the given {pixel}
        """
        # get the pixel value
        _, _, amplitude, phase = self.profile(points=[pixel])[0]

        # report the amplitude
        yield "amplitude", [(amplitude, "")]
        # and the phase
        yield "phase", [(phase, "")]

        # all done
        return

    def profile(self, points, closed=False):
        """
        Sample my data along the path defined by {points}
        """
        # ask my data manager to build a profile
        profile = qed.libqed.isce2.unwrapped.profile(
            source=self.data, points=points, closed=closed
        )
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

    def summary(self):
        """
        Build a sequence of the important channels that form my summary view
        """
        # get my channels
        channels = self.channels

        # use my amplitude
        yield channels["amplitude"]
        # and my phase
        yield channels["phase"]

        # as the only important channels
        return

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
        self.stats = self._collectStatistics()
        # populate my channels
        self._registerChannels()

        # all done
        return

    # implementation details
    def _open(self):
        """
        Initialize my data source
        """
        # grab my uri
        uri = self.uri
        # we only support local datasets; if the {uri} points to anything else
        if uri.scheme != "file":
            # make a channel
            channel = journal.error("qed.readers.native")
            # complain
            channel.line(f"while looking for {uri}")
            channel.line(f"unsupported scheme '{uri.scheme}' in the dataset URI")
            channel.line(f"the isce2.unw reader supports local datasets only")
            channel.line(
                f"please specify 'file:' as the dataset scheme, or drop it altogether"
            )
            # flush
            channel.log()
            # and bail
            return

        # grab the path to the dataset
        path = str(uri.address)
        # build the name of the buffer factory
        memoryType = f"{self.cell.tag}ConstMap"
        # look up the factory in the {pyre::memory} bindings
        bufferFactory = getattr(qed.libpyre.memory, memoryType)
        # make the memory buffer
        buffer = bufferFactory(path)

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

    def _collectStatistics(self):
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
        center = tuple((s - t) // 2 for s, t in zip(shape, tile))

        # make a pile for the channel stats
        stats = []
        # go through my two channels
        for channel in range(2):
            # inject the index of the {channel} into the center index
            center = qed.libpyre.grid.Index3D(index=(center[0], channel, center[1]))
            # extend the tile shape
            tile = qed.libpyre.grid.Shape3D(shape=(tile[0], 1, tile[1]))
            # compute the stats
            channelStats = qed.libqed.isce2.unwrapped.stats(
                source=data, origin=center, shape=tile
            )
            # and add them to the pile
            stats.append(channelStats)

        # and return them
        return stats

    def _registerChannels(self):
        """
        Register my channels
        """
        # go through the registry
        for channel in channelRegistry():
            # instantiate a workflow
            pipeline = channel(name=f"{self.pyre_name}.{channel.tag}")
            # autotune
            pipeline.autotune(stats=self.stats)
            # and register it
            self.channels[channel.tag] = pipeline
        # all done
        return


# end of file
