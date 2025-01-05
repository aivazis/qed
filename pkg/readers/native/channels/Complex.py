# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.native.complex"):
    """
    Make a visualization pipeline to display complex values
    """

    # configurable state
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the amplitude of values to render"

    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"

    saturation = qed.protocols.controller(default=qed.controllers.value)
    saturation.doc = "the saturation"

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super().autotune(**kwds)
        # notify my range
        self.amplitude.autotune(**kwds)
        # if i'm supposed
        if self.phase.auto:
            # adjust my phase
            self.phase.min = 0
            self.phase.low = 0
            self.phase.max = 1
            self.phase.high = 1
        # if i'm supposed
        if self.saturation.auto:
            # adjust my saturation
            self.saturation.value = 1
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my range
        yield self.amplitude, self.pyre_trait(alias="amplitude")
        # my phase
        yield self.phase, self.pyre_trait(alias="phase")
        # and my saturation
        yield self.saturation, self.pyre_trait(alias="saturation")
        # all done
        return

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # easy enough
        return pixel

    def project(self, pixel):
        """
        Represent a {pixel} as a complex number
        """
        # only one rep
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
        lowPhase = self.phase.low
        highPhase = self.phase.high
        saturation = self.saturation.value
        # add my configuration and chain up
        return super().tile(
            min=low,
            max=high,
            minPhase=lowPhase,
            maxPhase=highPhase,
            saturation=saturation,
            **kwds
        )

    # constants
    tag = "complex"


# end of file
