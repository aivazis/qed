# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Mask import Mask


# the mask of a GCOV product
class GCOVMask(Mask, family="qed.datasets.nisar.products.gcovmask"):
    """
    The mask of a GCOV product: a single-digit code naming the subswath of each valid sample,
    with 0 marking invalid samples and 255 marking pixels outside the acquisition extent
    """

    # implementation details
    def _retrieveChannels(self):
        """
        Generate a sequence of channel pipelines for this product
        """
        # i render through the GCOV mask channel
        yield "gcov"
        # all done
        return


# end of file
