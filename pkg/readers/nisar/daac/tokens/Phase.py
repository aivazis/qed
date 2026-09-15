# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the mission phase
class Phase(Numeric):
    """
    The mission phase
    """

    # metamethods
    def __init__(self, default=0, **kwds):
        # chain up
        super().__init__(default=default, low=0, high=4, width=1, **kwds)
        # set up my docstring
        self.__doc__ = "mission phase"
        # all done
        return


# end of file
