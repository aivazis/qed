# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Product import Product


# a NISAR unwrapped interferogram
class UNW(Product, family="qed.datasets.nisar.products.unw"):
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
        # make it available
        yield "phase", [(value, "")]
        # all done
        return

    # implementation details
    def _retrieveChannels(self):
        """
        Generate a sequence of channel pipelines for this product
        """
        # i only have one
        yield "unwrapped"
        # all done
        return


# end of file
