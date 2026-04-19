# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Product import Product


# the base class for NISAR bit masks
class Mask(Product, family="qed.datasets.nisar.products.mask"):
    """
    A bit mask
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "uint8"
    cell.doc = "the type of the dataset payload"

    # constants
    # the in-memory data layout of NISAR masks
    datatype = qed.h5.memtypes.uint8

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
        # now, go through my channels
        for name, channel in channels.items():
            # and ask each one for {value} representations
            yield name, channel.project(pixel=value)

        # all done
        return

    # implementation details
    # implementation details
    def _retrieveChannels(self):
        """
        Generate a sequence of channel pipelines for this product
        """
        # i only have one
        yield "valid"
        # all done
        return


# end of file
