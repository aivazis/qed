# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal
from osgeo import gdal


# a dataset in a binary file with no metadata
class GDALBand(
    qed.flow.product,
    family="qed.datasets.native.gdal",
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
        value = self.data.ReadAsArray(pixel[1], pixel[0], 1, 1)[0, 0]

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
        return []

    def render(self, channel, zoom, origin, shape):
        """
        Render a tile of the given specification
        """
        # interpret the zoom level as a scale
        scale = [1 << level for level in zoom]
        # scale up the origin
        scaledOrigin = [s * value for s, value in zip(scale, origin)]
        # and the shape
        scaledShape = [s * value for s, value in zip(scale, shape)]
        # get the data
        tile = self.data.ReadAsArray(
            scaledOrigin[1], scaledOrigin[0], scaledShape[1], scaledShape[0]
        )
        # the range to stretch across comes from the controller the client manipulates,
        # not from my own sample: a worker renders with the client's settings, and reading
        # my statistics here would silently ignore them
        low = channel.range.low
        high = channel.range.high
        # zoom
        zoomedTile = tile[:: scale[1], :: scale[0]]
        # render a tile and return it
        return channel.gdal(source=zoomedTile, shape=shape, low=low, high=high)

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
        # get the factory from my bindings
        cls = qed.readers.native.channels.value
        # instantiate it
        pipeline = cls(name=f"{context}.{cls.tag}")
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
        # ask gdal for the band statistics
        self.stats = self._collectStatistics()
        # and let my channels tune themselves against what it reported
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
    def __init__(self, rid=None, dataset=None, hydrated=False, seed=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # my statistics are whatever i was handed: a survey seed when i am a twin, and
        # nothing at all when i am live, until somebody asks me to measure
        self.stats = seed
        # a live band reads its layout out of the file
        if not hydrated:
            # get my band
            band = dataset.GetRasterBand(rid + 1)
            # store my data object
            self.data = band
            # set up my cell
            self.cell = gdal.GetDataTypeName(band.DataType).lower()
            # store my shape
            self.shape = dataset.RasterYSize, dataset.RasterXSize
            # set up my selector
            self.selector["band"] = rid
        # a twin holds no payload; its layout arrived in the record that built it
        else:
            # so there is nothing to open
            self.data = None

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

    def _collectStatistics(self):
        """
        Compute statistics on a sample of my data
        """
        # ask gdal, which reports over the whole band rather than a window of it
        min, max, mean, *_ = self.data.GetStatistics(True, True)
        # and return them
        return min, mean, max


# end of file
