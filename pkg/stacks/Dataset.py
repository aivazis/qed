# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# the channels that supply my aggregate pipelines
from qed.readers.nisar.products import channels


# the aggregate dataset of a stack
class Dataset(
    qed.flow.product, family="qed.datasets.stack", implements=qed.protocols.dataset
):
    """
    A dataset that renders aggregate views over the members of a stack
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = None
    cell.doc = "the type of the dataset payload"

    # the channels i support
    channels = qed.properties.dict(schema=qed.protocols.channel())
    channels.default = {}
    channels.doc = "the table of channels supported by this dataset"

    # the smallest possible index
    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = 0, 0
    origin.doc = "the smallest possible index"

    # the extent of the data
    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    # the selector that picks me out of my stack
    selector = qed.properties.kv()
    selector.default = {}
    selector.doc = "a key/value map that identifies the dataset to its stack"

    # the preferred subset shape
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

    def render(self, channel, zoom, origin, shape, mask=None, **kwds):
        """
        Render a tile of the given specification

        When {mask} is given, it is a per-member boolean selecting the subset that participates
        in the aggregate; my full membership stands when it is absent.
        """
        # if a participation mask was supplied
        if mask is not None:
            # reduce my members to the participating subset, preserving their order
            kwds["members"] = [
                member for member, on in zip(self.members, mask) if on
            ]
        # hand the request to the channel, pointing it at me as the source of members
        return channel.tile(
            source=self,
            datatype=self.datatype.htype,
            zoom=zoom,
            origin=origin,
            shape=shape,
            **kwds,
        )

    def pipelines(self, context):
        """
        Build my aggregate visualization pipelines using the given naming {context}
        """
        # go through the aggregate channels i provide
        for channel in self._retrieveChannels():
            # get the factory from the channels package
            cls = getattr(channels, channel)
            # instantiate it, naming it after its {tag} so the view can look it up by tag
            pipeline = cls(name=f"{context}.{cls.tag}")
            # autotune it from my sample
            pipeline.autotune(stats=self.stats)
            # and make it available
            yield pipeline
        # all done
        return

    def summary(self):
        """
        Build a sequence of the important channels that form my summary view
        """
        # for now, that is simply all of my channels
        yield from self.channels.values()
        # all done
        return

    def peek(self, pixel):
        """
        Build a family of value representations at the given {pixel}
        """
        # report the cursor position
        yield "cursor", [(f"{pixel}", "pixel")]
        # all done
        return

    def profile(self, points, closed=False):
        """
        Sample my data along the path defined by {points}
        """
        # until aggregate profiling exists, borrow the first member's view
        head, *_ = self.members
        # and let it sample
        return head.profile(points=points, closed=closed)

    # metamethods
    def __init__(self, members, **kwds):
        # chain up
        super().__init__(**kwds)
        # save my members
        self.members = members
        # single out the first one as my reference
        head, *_ = members
        # borrow its in-memory layout
        self.datatype = head.datatype
        # its cell type
        self.cell = head.cell
        # its extent
        self.shape = head.shape
        # its origin
        self.origin = head.origin
        # its preferred tile
        self.tile = head.tile
        # sample the aggregate to get statistics to autotune against
        self.stats = self._collectStatistics()
        # populate my channel pipelines
        self._registerChannels()
        # all done
        return

    # implementation details
    def _collectStatistics(self):
        """
        Sample the mean power over my members to set a sensible default rendering range
        """
        # my reference member
        head, *_ = self.members
        # test stand-ins carry no live data, so fall back to a member's own sample
        if not hasattr(head, "data"):
            # which is the best we can do without data
            return head.stats
        # gather the member data sources
        sources = [member.data.dataset for member in self.members]
        # make a sample tile that fits within my shape
        tile = tuple(min(256, extent) for extent in self.shape)
        # centered in my shape
        center = tuple((extent - t) // 2 for extent, t in zip(self.shape, tile))
        # as a grid index
        center = qed.libpyre.grid.Index2D(index=center)
        # and a grid shape
        tile = qed.libpyre.grid.Shape2D(shape=tile)
        # sample the per-pixel mean power over my members
        return qed.libqed.nisar.stack.stats(
            sources=sources, datatype=self.datatype.htype, origin=center, shape=tile
        )

    def _registerChannels(self):
        """
        Build the channel pipelines
        """
        # build my default pipelines
        for pipeline in self.pipelines(context=self.pyre_name):
            # and register each under its tag
            self.channels[pipeline.tag] = pipeline
        # all done
        return

    def _retrieveChannels(self):
        """
        Generate a sequence of the aggregate channels this dataset provides
        """
        # the mean power of the stack
        yield "meanpower"
        # and its temporal coherence
        yield "stackCoherence"
        # all done
        return


# end of file
