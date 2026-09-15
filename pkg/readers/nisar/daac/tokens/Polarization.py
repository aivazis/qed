# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the polarization
class Polarization(Discrete, qed.properties.str):
    """
    The polarization type
    """

    # properties
    @property
    def doc(self):
        """
        Set up my docstring
        """
        # inject my name
        return self.name

    # metamethods
    def __init__(self, allowed, **kwds):
        # chain up
        super().__init__(default=allowed[0], allowed=allowed, **kwds)
        # all done
        return


# end of file
