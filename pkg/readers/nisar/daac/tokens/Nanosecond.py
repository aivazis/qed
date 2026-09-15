# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the nanosecond of the file creation timestamp
class Nanosecond(Numeric):
    """
    The nanosecond of the file creation timestamp
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(default=0, low=0, high=1000000000, width=9, **kwds)
        # set up my docstring
        self.__doc__ = "nanosecond"
        # all done
        return


# end of file
