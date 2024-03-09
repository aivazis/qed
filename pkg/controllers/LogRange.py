# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import math

# support
import qed

# superclass
from .Controller import Controller


# a channel for displaying the amplitude of complex values
class LogRange(Controller, family="qed.controllers.logrange"):
    """
    Configuration for a channel with logarithmic data
    """

    # user configurable state, in log scale
    low = qed.properties.float(default=-6)
    low.doc = "the lowest value; anything below is underflow"

    high = qed.properties.float(default=3)
    high.doc = "the highest value; anything above is overflow"

    min = qed.properties.float(default=-7)
    min.doc = "the smallest possible value"

    max = qed.properties.float(default=4)
    max.doc = "the largest possible value"

    # interface
    def updateRange(self, low, high):
        """
        Update my state with new values for the range
        """
        # update my state
        self.low = low
        self.high = high

        # and let the caller know
        return True

    # helpers
    def _autotune(self, stats, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super()._autotune(stats=stats, **kwds)

        # unpack the stats
        low, mean, high = stats
        # if low is too small
        if low / high < 1e-3:
            # adjust it
            low = high / 1e3

        # we want to be conservative, as this logic is only supposed to make sure that
        # the initial display is sensible; to this end, we leave both values at the low end
        # of the range at their default values

        # at the low end, scale the mean down a bit to form the initial guess
        self.low = math.log10(mean / 7)
        # and, if necessary, adjust the minimum value
        self.min = math.floor(min(self.low, math.log10(low)))
        # at the other end, scale the mean up a bit
        self.high = math.log10(7 * mean)
        # and adjust the max value to the next higher power of 10
        self.max = math.ceil(max(self.high, math.log10(high)))

        # all done
        return

    # constants
    tag = "range"


# end of file
