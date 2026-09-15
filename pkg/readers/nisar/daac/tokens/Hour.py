# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the hour of the file creation timestamp
class Hour(Numeric):
    """
    The hour of the file creation timestamp
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(default=0, low=0, high=24, width=2, **kwds)
        # set up my docstring
        self.__doc__ = "hour"
        # all done
        return


# end of file
