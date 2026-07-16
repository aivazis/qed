# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for GUNW product masks
class GUNWMask(Channel, family="qed.channels.nisar.gunwmask"):
    """
    Make a visualization pipeline to display a GUNW product mask
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
    tag = "gunw"
    category = "masks"


# end of file
