# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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

    def render(self, channel, zoom, origin, shape, **kwds):
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
            **kwds,
        )

    def sample(self, zoom: tuple, origin: tuple, shape: tuple) -> tuple:
        """
        Collect a mergeable statistical sample of the tile at {origin}+{shape}, visiting
        exactly the decimated footprint the render at this {zoom} sees
        """
        # take the same source the render took: a sample that strided the product while
        # the render read a decimated level would undo the saving entirely, and would be
        # measuring the same cells the long way round
        data, residual = self.resolve(zoom=zoom)
        # what is left of the zoom becomes the striding
        stride = tuple(2**level for level in residual)
        # sample the strided footprint and return the mergeable record
        return qed.libqed.nisar.sample(
            source=data,
            datatype=self.datatype.htype,
            origin=origin,
            shape=shape,
            stride=stride,
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

    def resolve(self, zoom: tuple) -> tuple:
        """
        Report the source that serves a render at {zoom}, and the zoom still to apply to it

        Ordinarily that is my own payload, owing the whole decimation. When a pyramid has
        been built for me, a zoomed out request is served instead by the level nearest to
        what it asked for, which holds the decimated cells already: the render then reads a
        small dataset at a small stride rather than striding a large one, and a strided read
        of a chunked product decompresses every chunk its footprint covers whether it keeps
        the cells or not. The pixels are the same either way -- a level is cell for cell
        what striding the base produces -- so nothing above here needs to know which
        answered
        """
        # a dataset with no pyramid answers for itself
        if self.pyramid is None:
            # owing the whole decimation
            return self.data.dataset, tuple(zoom)
        # otherwise, let the pyramid pick the level and say what is left over
        return self.pyramid.level(zoom=zoom)

    def measure(self):
        """
        Collect the statistics my channels tune themselves from, and tune them

        Construction deliberately leaves me unmeasured: reading my payload is the expensive
        part, and the two contexts that build me without needing it -- a worker rendering a
        tile, which is about to be handed the client's controller state, and a twin
        hydrated from a survey, which carries statistics already -- would both pay for
        nothing. Whoever wants me tuned from my own data asks for it
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
    def __init__(self, data=None, hydrated=False, seed=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the dataset; a metadata-only twin has none
        self.data = data
        # my statistics are whatever i was handed: a survey seed when i am a twin, and
        # nothing at all when i am live, until somebody asks me to measure
        self.stats = seed
        # the decimated levels of my data, when somebody has built and handed me them
        self.pyramid = None
        # a live dataset takes its tiling from the file
        if not hydrated:
            # ask {h5} for its on-disk layout
            layout = data.dcpl.layout
            # if it is chunked
            if layout == qed.h5.libh5.Layout.chunked:
                # adjust my tile to match the dataset chunk size
                self.tile = data.chunk
        # populate my channel pipelines
        self._registerChannels()

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
        Collect statistics by probing my data in several places
        """
        # geocoded products frame their data inside a much larger grid of fill, so a single
        # window in the middle finds nothing at all on some of them; probe a spread of
        # windows instead, which costs about the same and finds data wherever it sits
        return qed.readers.probe(dataset=self)


# end of file
