# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Product import Product


# a NISAR unwrapped interferogram
class Coherence(Product, family="qed.datasets.nisar.products.coherence"):
    """
    An UNW dataset
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "real32"
    cell.doc = "the type of the dataset payload"

    # constants
    # the in-memory data layout of NISAR unwrapped interferograms
    datatype = qed.h5.memtypes.float32

    # interface
    def peek(self, pixel):
        """
        Build a family of value representations at the given {pixel}
        """
        # generate cursor information
        yield from self.cursor(pixel=pixel)

        # get the value of the {pixel}
        _, _, value = self.profile(points=[pixel])[0]
        # get my channels
        channels = self.channels
        # get the {unwrapped} channel
        coherence = channels["coherence"]
        # project
        yield "coherence", coherence.project(pixel=value)
        # all done
        return

    def render(self, **kwds):
        """
        Render a tile of the given specification
        """
        # render a tile and return it
        return super().render(mask=self.mask.dataset, **kwds)

    def __init__(self, mask, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the mask
        self.mask = mask
        # all done
        return

    # implementation details
    def _retrieveChannels(self):
        """
        Generate a sequence of channel pipelines for this product
        """
        # the coherence
        yield "coherence"
        # all done
        return


# end of file
