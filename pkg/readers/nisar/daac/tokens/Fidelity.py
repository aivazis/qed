# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the product accuracy and fidelity
class Fidelity(Discrete, qed.properties.str):
    """
    The product accuracy and fidelity
    """

    # metamethods
    def __init__(self, allowed, **kwds):
        # chain up
        super().__init__(default=allowed[0], allowed=allowed, **kwds)
        # set up my docstring
        self.__doc__ = "accuracy/fidelity"
        # all done
        return


# end of file
