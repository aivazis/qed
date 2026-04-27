# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import math
import qed

# superclass
from .Channel import Channel


# a channel for displaying conherence values
class Coherence(Channel, family="qed.channels.nisar.coherence"):
    """
    Make a visualization pipeline to display the coherence
    """

    # user configurable state
    range = qed.protocols.controller(default=qed.controllers.linearRange)
    range.doc = "the manager of the range of values to render"

    # interface
    def autotune(self, **kwds):
        # chain up
        super().autotune(**kwds)
        # notify my range
        self.range.autotune(**kwds)
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my value
        yield self.range, self.pyre_trait(alias="range")
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
        low = self.range.low
        high = self.range.high
        # make a tile and return it
        return super().tile(min=low, max=high, **kwds)

    # constants
    tag = "coherence"
    category = "real"


# end of file
