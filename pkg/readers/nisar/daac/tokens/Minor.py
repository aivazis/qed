# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the minor release
class Minor(Numeric):
    """
    The minor release
    """

    # metamethods
    def __init__(self, default=0, **kwds):
        # chain up
        super().__init__(default=default, low=0, high=10, width=1, **kwds)
        # set up my docstring
        self.__doc__ = "minor release"
        # all done
        return


# end of file
