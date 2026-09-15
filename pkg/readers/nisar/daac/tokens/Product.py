# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the product type
class Product(Discrete, qed.properties.str):
    """
    The product type
    """

    # metamethods
    def __init__(self, product, **kwds):
        # chain up
        super().__init__(default=product, allowed=(product,), **kwds)
        # set up my docstring
        self.__doc__ = "product type"
        # all done
        return


# end of file
