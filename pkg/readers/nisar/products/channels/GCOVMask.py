# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for GCOV product masks
class GCOVMask(Channel, family="qed.channels.nisar.gcovmask"):
    """
    Make a visualization pipeline to display a GCOV product mask
    """

    # interface
    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # i don't have any controllers
        return []

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # easy enough
        return pixel

    def project(self, pixel):
        """
        Compute the representation of a {pixel}
        """
        # only one rep
        yield pixel, ""
        # all done
        return

    # constants
    tag = "gcov"
    category = "masks"


# end of file
