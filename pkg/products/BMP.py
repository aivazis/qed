# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Product import Product


# an image that can be shipped to the client
class BMP(
    Product, family="qed.products.bitmaps.bmp", implements=qed.protocols.products.image
):
    """
    A microsoft v2 bitmap
    """


# end of file
