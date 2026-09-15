# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the satellite direction of movement
class Direction(Discrete, qed.properties.str):
    """
    The satellite direction of movement
    """

    # constants
    allowed = ("A", "D")

    # metamethods
    def __init__(self, default=allowed[0], allowed=allowed, **kwds):
        # chain up
        super().__init__(default=default, allowed=allowed, **kwds)
        # set up my docstring
        self.__doc__ = "direction"
        # all done
        return


# end of file
