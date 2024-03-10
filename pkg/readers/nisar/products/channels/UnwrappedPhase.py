# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import math
import qed

# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class UnwrappedPhase(Channel, family="qed.channels.isce2.int.phase"):
    """
    Make a visualization pipeline to display the phase of complex values
    """

    # user configurable state
    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"

    brightness = qed.protocols.controller(default=qed.controllers.value)
    brightness.doc = "the brightness"

    # interface
    def autotune(self, **kwds):
        # chain up
        super().autotune(**kwds)
        # notify my range
        self.phase.autotune(**kwds)
        # if my brightness needs autotuning
        if self.brightness.auto:
            # adjust it to the middle of the scale
            self.brightness.value = 0.5
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my phase
        yield self.phase, self.pyre_trait(alias="phase")
        # my brightness
        yield self.brightness, self.pyre_trait(alias="brightness")
        # all done
        return

    def eval(self, phase):
        """
        Get the phase of the pixel
        """
        # easy enough
        return phase

    def project(self, pixel):
        """
        Compute the phase of a {pixel}
        """
        # get π
        π = math.pi
        # get the value of the phase, in radians per the spec
        value = pixel
        # project to π radians
        value = value / π

        # project
        # in π radians
        yield value, "π radians"
        # in degrees in [0, 360]
        yield 180 * value, "degrees"
        # in cycles, in [0,1]
        yield value / 2, "cycles"

        # all done
        return

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # unpack my configuration
        low = self.phase.low
        high = self.phase.high
        brightness = self.brightness.value
        # make a tile and return it
        return super().tile(min=low, max=high, brightness=brightness, **kwds)

    # constants
    tag = "unwrapped"
    category = "real"


# end of file
