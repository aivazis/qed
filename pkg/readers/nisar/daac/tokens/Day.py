# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the day of the year
class Day(Numeric):
    """
    The day of the year
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(default=1, low=1, high=367, width=3, **kwds)
        # set up my docstring
        self.__doc__ = "day of year"
        # all done
        return


# end of file
