# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import journal

# support
import qed


# a dataset in a binary file with no metadata
class MemoryMap(
    qed.flow.product,
    family="qed.datasets.native.mmap",
    implements=qed.protocols.dataset,
):
    """
    A dataset in a flat binary file
    """

    # public data
    # the source
    uri = qed.properties.uri()
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
        # get my data type
        cell = self.cell
        # my channels
        channels = self.channels
        # and the value of the {pixel}
        _, _, value = self.profile(points=[pixel])[0]

        # build the cursor rep
        yield "cursor", [(f"{pixel}", "pixel")]

        # go through the channels marked as special by my data type
        for name in cell.summary:
            # get the corresponding channel
            channel = channels[name]
            # and ask each one for {value} representations
            yield name, channel.project(pixel=value)

        # all done
        return

    def profile(self, points, closed=False):
        """
        Sample my data along the path defined by {points}
        """
        # ask my data manager to build a profile
        profile = qed.libqed.native.profile(
            source=self.data, points=points, closed=closed
        )
        # and return it
        return profile

    def render(self, channel, zoom, origin, shape):
        """
        Render a tile of the given specification
        """
        # render a tile and return it
        return channel.tile(source=self, zoom=zoom, origin=origin, shape=shape)

    def summary(self):
        """
        Build a sequence of the important channels that form my summary view
        """
        # get my channels
        channels = self.channels
        # ask my cell type for its list
        for name in self.cell.summary:
            # resolve into the actual channel
            channel = channels[name]
            # and make it available
            yield channel

        # all done
        return

    def pipelines(self, context):
        """
        Build my standard visualization pipelines using the given naming {context}
        """
        # go through the default channels provided by my data type
        for channel in self.cell.channels:
            # get the factory from my bindings
            cls = getattr(qed.readers.native.channels, channel)
            # instantiate it
            pipeline = cls(name=f"{context}.{channel}")
            # autotune it, if necessary
            pipeline.autotune(stats=self.stats)
            # and make it available
            yield pipeline
        # all done
        return

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # build my data object
        self.data = self._open()
        # get stats on a sample of my data
        self.stats = self._collectStatistics()

        # build my default pipelines
        for pipeline in self.pipelines(context=self.pyre_name):
            # and register them
            self.channels[pipeline.tag] = pipeline

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
            channel.line(f"the native reader supports local datasets only")
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

        # realize the dataset shape
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
        center = tuple((s - t) // 2 for s, t in zip(shape, tile))

        # convert to a grid index
        center = qed.libpyre.grid.Index2D(index=center)
        # and a shape
        tile = qed.libpyre.grid.Shape2D(shape=tile)
        # compute the stats
        stats = qed.libqed.native.stats(source=data, origin=center, shape=tile)
        # and return them
        return stats


# end of file
