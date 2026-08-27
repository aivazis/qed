# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Controller import Controller


# a mixin for a channel with rel values in a linear range
class LinearRange(Controller, family="qed.controllers.linearrange"):
    """
    Configuration for a channel with data in a linear range
    """

    # user configurable state
    low = qed.properties.float(default=None)
    low.doc = "the lowest value; anything below is underflow"

    high = qed.properties.float(default=None)
    high.doc = "the highest value; anything above is overflow"

    min = qed.properties.float(default=-1.0e3)
    min.doc = "the smallest possible value"

    max = qed.properties.float(default=1.0e3)
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
        # compute the spread
        spread = high - low

        # set the initial guess for the low value
        self.low = low
        # and prime the minimum
        self.min = mean - 2 * spread
        # similarly
        self.high = high
        # use the opposite for the high end
        self.max = mean + 2 * spread
        # all done
        return

    def _widen(self, stats: tuple) -> bool:
        """
        Expand my bounds to accommodate {stats}, the accumulated whole-dataset statistics
        """
        # unpack the stats
        low, mean, high = stats
        # measure the current span
        span = self.max - self.min
        # small escapes are tolerated; the slack provides hysteresis
        slack = 0.05 * span if span > 0 else 0.0
        # if the current bounds accommodate the data to within the slack
        if low >= self.min - slack and high <= self.max + slack:
            # nothing to do
            return False
        # form the widened extent
        lowest = min(self.min, low)
        highest = max(self.max, high)
        # with some breathing room, so the next small escape doesn't move them again
        margin = 0.05 * (highest - lowest)
        # bounds adjustments are presentation only, so my dirty flag must survive them
        marked = self.dirty
        # widen whichever end the data escaped
        if low < self.min - slack:
            # the bottom
            self.min = lowest - margin
        if high > self.max + slack:
            # the top
            self.max = highest + margin
        # restore the flag
        self.dirty = marked
        # report the move
        return True

    # constants
    tag = "range"


# end of file
