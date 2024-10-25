# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# superclass
from .Specification import Specification


# specification for a block of data
class Tile(Specification, family="qed.products.tiles"):
    """
    A tile is an n-dimensional block of typed data
    """


# end of file
