# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the acquisition mode
class Acquisition(Discrete, qed.properties.str):
    """
    The acquisition mode identifier
    """

    # constants
    allowed = ("A", "M")

    # metamethods
    def __init__(self, default=allowed[0], allowed=allowed, **kwds):
        # chain up
        super().__init__(default=default, allowed=allowed, **kwds)
        # set up my docstring
        self.__doc__ = "acquisition mode"
        # all done
        return


# end of file
