# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# superclass
from .Imaginary import Imaginary


# a channel for displaying the imaginary part of BFPQ encoded complex values
class BFPQImaginary(Imaginary, family="qed.channels.nisar.bfpq-imaginary"):
    """
    Make a visualization pipeline to display the imaginary part of BFPQ encoded complex values
    """

    # interface
    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # add my configuration and chain up
        return super().tile(bfpq=self.bfpq, **kwds)

    # metamethods
    def __init__(self, bfpq, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the lookup table
        self.bfpq = bfpq
        # all done
        return

    # constants
    category = "bfpq"


# end of file
