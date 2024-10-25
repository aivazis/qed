# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Specification import Specification


# specification for a block of data
class Image(Specification, family="qed.products.images"):
    """
    A rendering of a data tile as an image to be displayed by the client
    """

    @classmethod
    def pyre_default(cls, **kwds):
        """
        The default image
        """
        # is a microsoft v2 bitmap
        return qed.products.bmp


# end of file
