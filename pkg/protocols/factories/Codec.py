# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
from .. import products

# superclass
from .Producer import Producer


# a producer of bitmaps that the client can render
class Codec(Producer, family="qed.factories.codecs"):
    """
    A factory of bitmaps for the client-side rendering engine
    """

    # required state
    # output
    bmp = products.image.output()
    bmp.doc = "the image that will be sent to the client"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Provide a default implementation
        """
        # default to the microsoft BMP encoder
        return qed.factories.bmp


# end of file
