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

    @property
    def kernels(self):
        """
        The raster kernels that read my cells the way my file stores them
        """
        # my in-memory layout names the cell type, in the vocabulary the kernels are
        # gathered under. a product whose samples are encoded rather than stored -- the
        # quantized pairs of a BFPQ raster, which only the lookup table turns into numbers
        # -- has no native cell, and so has no kernel that could read it as it stands
        cell = self.datatype.cell
        # if there is no name
        if cell is None:
            # there is no kernel either; whoever needs one must decode first
            return None
        # the kernels live in the extension; its absence must be named rather than tripped
        # over, since an attribute error raised here would be reported as the absence of
        # this very property
        if qed.libqed is None:
            # complain, quoting the loader
            raise qed.exceptions.ExtensionError(
                reason=f"{qed.ext.libqed_error}; the cells of '{self.pyre_name}' cannot be read"
            )
        # otherwise, hand back the set that matches
        return getattr(qed.libqed.nisar.cells, cell, None)

    @property
    def fill(self) -> float:
        """
        The magnitude of the value my product declared it writes where it has nothing to say

        A render uses this to tell the two kinds of absence apart: a cell holding exactly
        this value is absence the file admits to, while a nan where this is something else
        is absence it does not -- which is a bug in whatever wrote the product, and invisible
        from the metadata alone. It is the magnitude rather than the value because a complex
        fill and a real one have to be judged by the same measure, and the parts of a fill
        carry no meaning of their own
        """
        # a metadata-only twin has no file to ask; it also never renders, since tiles are
        # produced by crews holding their own copy of the product
        if self.data is None:
            # so nothing it could be asked about would match
            return float("nan")
        # ask the product, and reduce the answer the way the kernels reduce a cell
        return abs(self.data.dataset.fillValue)

    # interface
    def channel(self, name):
        """
        Get the visualization workflow for the given {channel}
        """
        # look up the channel and return it
        return self.channels[name]

    def companions(self):
        """
        Report the rasters a render of mine reads alongside my payload

        A masked channel pairs each of my cells with the cell of the mask at the same place,
        and the kernel reads the two with one origin and one stride. Naming them here is
        what lets my levels and theirs be chosen together: a render that took its data from
        a decimated level while the mask still came from the product would pair every cell
        with the wrong mask value
        """
        # ordinarily a dataset is read by itself
        return {}

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
        # the kernels that can read my cells
        kernels = self.kernels
        # a product no kernel can read as it stands measures nothing here; an encoded one
        # overrides me with the kernel that knows how to decode it
        if kernels is None:
            # hand back an empty record, which merges into an accumulator without moving it
            return 0.0, 0.0, 0.0, 0.0, 0.0
        # take the same source the render took: a sample that strided the product while
        # the render read a decimated level would undo the saving entirely, and would be
        # measuring the same cells the long way round
        data, _, residual = self.resolve(zoom=zoom)
        # what is left of the zoom becomes the striding
        stride = tuple(2**level for level in residual)
        # sample the strided footprint and return the mergeable record
        return kernels.sample(
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
        Report the sources that serve a render at {zoom}, and the zoom still to apply to them

        The answer is my payload, my companion rasters, and what is left of the decimation.
        Ordinarily the payload is my own dataset, owing the whole zoom. When a pyramid has
        been built for me, a zoomed out request is served instead by the level nearest to
        what it asked for, which holds the decimated cells already: the render then reads a
        small dataset at a small stride rather than striding a large one, and a strided read
        of a chunked product decompresses every chunk its footprint covers whether it keeps
        the cells or not. The pixels are the same either way -- a level is cell for cell
        what striding the base produces -- so nothing above here needs to know which
        answered.

        My companions come back at the same depth as my payload, because the kernel reads
        all of them with one origin and one stride. A companion that has not been decimated
        as deeply as i have therefore decides the matter for everybody, and the whole render
        falls back on the full resolution rasters
        """
        # the rasters that must be read alongside my payload
        companions = self.companions()
        # a dataset with no levels answers for itself, owing the whole decimation
        if self.pyramid is None:
            # so nothing is decimated
            source, residual = self.data.dataset, tuple(zoom)
        # otherwise, let the pyramid pick the level and say what is left over
        else:
            # by asking it
            source, residual = self.pyramid.level(zoom=zoom)
        # the depth of the level that answered, which is what the companions must match;
        # the levels halve both axes together, so either axis reports it
        exponent = zoom[0] - residual[0]
        # take the companions at that depth
        matched = self._companionsAt(companions=companions, exponent=exponent)
        # if one of them could not come along
        if matched is None:
            # then none of us does: the render reads everything off the product, which is
            # what it did before any of this existed
            return (
                self.data.dataset,
                self._companionsAt(companions=companions, exponent=0),
                tuple(zoom),
            )
        # otherwise, hand off the matched set
        return source, matched, tuple(residual)

    def at(self, exponent: int):
        """
        Report the source that holds my cells decimated by exactly {exponent} halvings, or
        nothing at all when i have no such level
        """
        # the zeroth level is the payload itself, which every dataset has
        if exponent == 0:
            # so hand it over
            return self.data.dataset
        # a dataset with no levels has nothing else to offer
        if self.pyramid is None:
            # so say so
            return None
        # otherwise, ask for exactly that one
        return self.pyramid.at(exponent=exponent)

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

    def _companionsAt(self, companions: dict, exponent: int):
        """
        Take my companion rasters at exactly {exponent} halvings, or report that one of them
        cannot come
        """
        # the pile
        matched = {}
        # go through them
        for name, companion in companions.items():
            # ask each for exactly that depth
            raster = companion.at(exponent=exponent)
            # one that does not have it decides the matter for all of us, since the kernel
            # reads every raster it is handed with one origin and one stride
            if raster is None:
                # so report that this depth is not available
                return None
            # otherwise it joins the render
            matched[name] = raster
        # hand off the matched set
        return matched

    def _collectStatistics(self):
        """
        Collect statistics by probing my data in several places
        """
        # geocoded products frame their data inside a much larger grid of fill, so a single
        # window in the middle finds nothing at all on some of them; probe a spread of
        # windows instead, which costs about the same and finds data wherever it sits
        return qed.readers.probe(dataset=self)


# end of file
