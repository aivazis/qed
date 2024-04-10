# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# my channels
from . import channels


# a NISAR SLC
class Product(
    qed.flow.product,
    family="qed.datasets.nisar.products",
    implements=qed.protocols.dataset,
):
    """
    The base class for NISAR datasets
    """

    # public data
    # the source
    uri = qed.properties.uri(scheme="file")
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
        # generate cursor information
        yield from self.cursor(pixel=pixel)

        # get my data type
        cell = self.cell
        # my channels
        channels = self.channels
        # and the value of the {pixel}
        _, _, value = self.profile(points=[pixel])[0]

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
        # resolve the name of the profile maker
        name = f"profile{self.cell.tag}"
        # look it up
        factory = getattr(qed.libqed.nisar, name)
        # ask it to build a profile
        profile = factory(
            source=self.data.dataset,
            datatype=self.datatype.htype,
            points=points,
            closed=closed,
        )
        # and return it
        return profile

    def cursor(self, pixel):
        """
        Render information about the cursor position
        """
        # build the cursor rep
        yield "cursor", [(f"{pixel}", "pixel")]
        # all done
        return

    def render(self, channel, zoom, origin, shape):
        """
        Render a tile of the given specification
        """
        # render a tile and return it
        return channel.tile(
            source=self,
            datatype=self.datatype.htype,
            zoom=zoom,
            origin=origin,
            shape=shape,
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
        for channel in self._retrieveChannels():
            # get the factory from my bindings
            cls = getattr(channels, channel)
            # instantiate it
            pipeline = cls(name=f"{context}.{channel}")
            # autotune it, if necessary
            pipeline.autotune(stats=self.stats)
            # and make it available
            yield pipeline
        # all done
        return

    # metamethods
    def __init__(self, data, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the dataset
        self.data = data
        # collect statistics from a sample of my data
        self.stats = self._collectStatistics()
        # populate my channel pipelines
        self._registerChannels()

        # all done
        return

    # implementation details
    def _registerChannels(self):
        """
        Build the channel pipelines
        """
        # build my default pipelines
        for pipeline in self.pipelines(context=self.pyre_name):
            # and register them
            self.channels[pipeline.tag] = pipeline
        # all done
        return

    def _retrieveChannels(self):
        """
        Generate a sequence of channel pipelines for this product
        """
        # by default, look to my cell type
        yield from self.cell.channels
        # all done
        return

    def _collectStatistics(self):
        """
        Collect statistics from a sample of my data
        """
        # get my data
        data = self.data
        # extract the underlying dataset
        source = data.dataset
        # and its shape
        shape = data.shape

        # make a tile that fits within my shape
        tile = tuple(min(256, s) for s in shape)
        # center it in my shape
        center = tuple((s - t) // 2 for s, t in zip(shape, tile))

        # convert to a grid index
        center = qed.libpyre.grid.Index2D(index=center)
        # and a shape
        tile = qed.libpyre.grid.Shape2D(shape=tile)
        # compute the stats
        stats = qed.libqed.nisar.stats(
            source=source, datatype=self.datatype.htype, origin=center, shape=tile
        )

        # and return them
        return stats


# end of file
