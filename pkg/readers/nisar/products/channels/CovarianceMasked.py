# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import math
import qed

# superclass
from .Channel import Channel


# a channel for displaying covariance values
class CovarianceMasked(Channel, family="qed.channels.nisar.covarianceMasked"):
    """
    Make a visualization pipeline to display the covariance
    """

    # user configurable state
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the range of values to render"

    # interface
    def autotune(self, **kwds):
        # chain up
        super().autotune(**kwds)
        # notify my amplitude
        self.amplitude.autotune(**kwds)
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my value
        yield self.amplitude, self.pyre_trait(alias="amplitude")
        # all done
        return

    def eval(self, value):
        """
        Get the value of the pixel
        """
        # easy enough
        return value

    def project(self, pixel):
        """
        Compute the value of a {pixel}
        """
        # easy enough
        yield pixel, ""
        # all done
        return

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # unpack my configuration
        low = 10**self.amplitude.low
        high = 10**self.amplitude.high
        # make a tile and return it
        return super().tile(min=low, max=high, **kwds)

    # constants
    tag = "covarianceMasked"
    category = "real"


# end of file
