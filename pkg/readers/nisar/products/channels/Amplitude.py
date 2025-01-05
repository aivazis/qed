# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Amplitude(Channel, family="qed.channels.nisar.amplitude"):
    """
    Make a visualization pipeline to display the amplitude of complex values
    """

    # configurable state
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the range of values to render"

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the amplitude configuration
        """
        # chain up
        super().autotune(**kwds)
        # notify my amplitude
        self.amplitude.autotune(**kwds)
        # all done
        return

    def controllers(self):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers()
        # my amplitude
        yield self.amplitude, self.pyre_trait(alias="amplitude")
        # all done
        return

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # easy enough
        return abs(pixel)

    def project(self, pixel):
        """
        Compute the amplitude of a {pixel}
        """
        # only one choice
        yield abs(pixel), ""
        # and done
        return

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # get my configuration
        low = 10**self.amplitude.low
        high = 10**self.amplitude.high
        # add my configuration and chain up
        return super().tile(min=low, max=high, **kwds)

    # constants
    tag = "amplitude"
    category = "slc"


# end of file
