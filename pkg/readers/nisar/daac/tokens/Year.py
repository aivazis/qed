# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the year
class Year(Numeric):
    """
    The year
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(default=2025, low=2025, high=10000, width=4, **kwds)
        # set up my docstring
        self.__doc__ = "year"
        # all done
        return


# end of file
