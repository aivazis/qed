# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Mask import Mask


# the mask of a GUNW product
class GUNWMask(Mask, family="qed.datasets.nisar.products.gunwmask"):
    """
    The mask of a GUNW product: a three-digit code combining the water flag with the reference
    and secondary RSLC subswath numbers
    """

    # implementation details
    def _retrieveChannels(self):
        """
        Generate a sequence of channel pipelines for this product
        """
        # i render through the GUNW mask channel
        yield "gunw"
        # all done
        return


# end of file
