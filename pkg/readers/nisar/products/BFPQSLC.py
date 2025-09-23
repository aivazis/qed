# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# superclass
from .Product import Product

# my channels
from . import channels


# a NISAR BFPQ encoded SLC
class BFPQSLC(Product, family="qed.datasets.nisar.products.bfpqslc"):
    """
    A BFPQ encoded SLC dataset
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"

    # constants
    # the in-memory data layout of BFPQ encoded NISAR complex data products
    datatype = qed.h5.memtypes.complexUInt16

    # interface
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
        # build a profile
        profile = qed.libqed.nisar.profileBFPQ(
            source=self.data.dataset,
            datatype=self.datatype.htype,
            bfpq=self.bfpq,
            points=points,
            closed=closed,
        )
        # and return it
        return profile

    def pipelines(self, context):
        """
        Build my visualization pipelines
        """
        # go through the default channels provided by my data type
        for channel in self._retrieveChannels():
            # get the factory from my bindings
            cls = getattr(channels, f"{channel}BFPQ")
            # instantiate it
            pipeline = cls(name=f"{context}.{channel}", bfpq=self.bfpq)
            # autotune it, if necessary
            pipeline.autotune(stats=self.stats)
            # and make it available
            yield pipeline
        # all done
        return

    # metamethods
    def __init__(self, bfpq, **kwds):
        # save the lookup table; do this before chaining up so my overrides have access
        # to the BFPQ lookup table
        self.bfpq = bfpq
        # chain up
        super().__init__(**kwds)
        # all done
        return

    # implementation details
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
        stats = qed.libqed.nisar.statsBFPQ(
            source=source,
            datatype=self.datatype.htype,
            bfpq=self.bfpq,
            origin=center,
            shape=tile,
        )

        # and return them
        return stats


# end of file
