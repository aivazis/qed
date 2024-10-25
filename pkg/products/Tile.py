# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Product import Product


# a block of data
class Tile(
    Product, family="qed.products.bitmaps.bmp", implements=qed.protocols.products.tile
):
    """
    An n-dimensional block of typed data
    """


# end of file
