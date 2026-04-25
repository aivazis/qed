# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for masks
class Raw(Channel, family="qed.channels.nisar.raw"):
    """
    Make a visualization pipeline to display masks
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
        Compute the real part of a {pixel}
        """
        # only one rep
        yield pixel, ""
        # all done
        return

    # constants
    tag = "raw"
    category = "mask"


# end of file
