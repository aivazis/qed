# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the PGE system used to create a product
class Environment(Discrete, qed.properties.str):
    """
    The PGE system used to create this product
    """

    # constants
    allowed = ("A", "D", "P", "T", "S", "X")

    # metamethods
    def __init__(self, default=allowed[0], allowed=allowed, **kwds):
        # chain up
        super().__init__(default=default, allowed=allowed, **kwds)
        # set up my docstring
        self.__doc__ = "environment"
        # all done
        return


# end of file
