# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the radar configuration mode
class RCID(Numeric):
    """
    The radar configuration mode
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(default=1, low=1, high=256, width=3, **kwds)
        # set up my docstring
        self.__doc__ = "rcid"
        # {eval} fails on expressions where integers have leading zeroes, so strip them
        self.converters.append(lambda value, **kwds: int(value))
        # all done
        return


# end of file
