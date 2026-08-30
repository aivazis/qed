# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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

    def sample(self, zoom: tuple, origin: tuple, shape: tuple) -> tuple:
        """
        Collect a mergeable statistical sample of the tile at {origin}+{shape}, visiting
        exactly the decimated footprint the render at this {zoom} sees
        """
        # the render pipeline decimates by striding
        stride = tuple(2**level for level in zoom)
        # sample the strided footprint and return the mergeable record
        return qed.libqed.native.sample(
            source=self.data, origin=origin, shape=shape, stride=stride
        )

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

    def measure(self):
        """
        Collect the statistics my channels tune themselves from, and tune them

        Construction deliberately leaves me unmeasured; whoever wants me tuned from my own
        data asks for it, so the contexts that do not need it -- a worker about to receive
        the client's controller state, a twin that carries a survey seed -- pay nothing
        """
        # a metadata-only twin has no payload to measure
        if self.data is None:
            # so it keeps the seed it was hydrated with
            return self.stats
        # sample my data
        self.stats = self._collectStatistics()
        # and let my channels tune themselves against what i found
        self._tuneChannels()
        # hand off the record
        return self.stats

    def survey(self):
        """
        Report what a client needs to know about me, without any of my payload
        """
        # my metadata travels as a finding i author myself, so my seed statistics arrive
        # in exactly the shape my channels expect
        return qed.nexus.finding(
            # the factory that materializes my twin
            factory=self.pyre_family(),
            # my layout
            cell=self.cell.pyre_family(),
            shape=tuple(self.shape),
            origin=tuple(self.origin),
            tile=tuple(self.tile),
            # the channels i support
            channels=tuple(self.channels.keys()),
            # and the statistics my channels tuned themselves against
            stats=self.stats,
        )

    # metamethods
    def __init__(self, hydrated=False, seed=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # my statistics are whatever i was handed: a survey seed when i am a twin, and
        # nothing at all when i am live, until somebody asks me to measure
        self.stats = seed
        # a live dataset lays a grid over its file; a twin holds no payload at all
        self.data = None if hydrated else self._open()

        # build my default pipelines
        for pipeline in self.pipelines(context=self.pyre_name):
            # and register them
            self.channels[pipeline.tag] = pipeline

        # all done
        return

    # implementation details
    def _tuneChannels(self):
        """
        Let my channel pipelines adjust themselves to my statistics
        """
        # go through my pipelines
        for pipeline in self.channels.values():
            # and let each one tune itself; a pipeline pinned by the user stays put
            pipeline.autotune(stats=self.stats)
        # all done
        return

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
        # lay an erased grid of my cell type over the memory-mapped file and return it; it presents
        # the buffer protocol, which is what the tile generators consume
        return qed.libpyre.grid.map(
            uri=path, shape=self.shape, cell=self.cell.cell, create=False
        )

    def _collectStatistics(self):
        """
        Compute statistics on a sample of my data
        """
        # a single window in the middle finds nothing on a raster whose data sits off
        # center; probe a spread of windows instead, which costs about the same
        return qed.readers.probe(dataset=self)


# end of file
