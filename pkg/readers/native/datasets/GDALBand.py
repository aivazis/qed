# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


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
        # unpack my range
        low, _, high = self.stats
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

    # metamethods
    def __init__(self, rid, dataset, **kwds):
        # chain up
        super().__init__(**kwds)
        # get my band
        band = dataset.GetRasterBand(rid + 1)
        # store my data object
        self.data = band
        # set up my cell
        self.cell = gdal.GetDataTypeName(band.DataType).lower()
        # store my shape
        self.shape = dataset.RasterYSize, dataset.RasterXSize
        # set up my selector
        self.selector["raster"] = rid

        # get stats on a sample of my data
        self.stats = self._collectStatistics()

        # build my default pipelines
        for pipeline in self.pipelines(context=self.pyre_name):
            # and register them
            self.channels[pipeline.tag] = pipeline

        # all done
        return

    # implementation details
    def _collectStatistics(self):
        """
        Compute statistics on a sample of my data
        """
        # get my stats
        min, max, mean, *_ = self.data.GetStatistics(True, True)
        # and return them
        return min, mean, max


# end of file
