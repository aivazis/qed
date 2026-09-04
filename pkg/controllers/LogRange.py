# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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
        # a sample with nothing positive in it, e.g. one taken from a raster that is all
        # zeros, has nothing to teach a log scale; the configured values stay in place, and
        # the accumulated statistics will widen the bounds if a tile ever finds something
        if high <= 0:
            # so leave things alone
            return
        # protect the low end from zeros and excessive dynamic range
        if low <= 0 or low / high < 1e-3:
            # by clipping it
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

    def _widen(self, stats: tuple) -> bool:
        """
        Expand my bounds to accommodate {stats}, the accumulated whole-dataset statistics
        """
        # unpack the stats, which arrive in linear scale
        low, mean, high = stats
        # a degenerate sample has nothing to teach a log scale
        if high <= 0:
            # so leave things alone
            return False
        # protect the low end from zeros and excessive dynamic range, like {_autotune} does
        if low <= 0 or low / high < 1e-3:
            # by clipping it
            low = high / 1e3
        # form the candidate bounds on whole decades, which provides natural hysteresis:
        # the bounds only move when the data escapes the current decade
        lowest = math.floor(math.log10(low))
        highest = math.ceil(math.log10(high))
        # if the current bounds already accommodate the data
        if lowest >= self.min and highest <= self.max:
            # nothing to do
            return False
        # bounds adjustments are presentation only, so my dirty flag must survive them
        marked = self.dirty
        # widen, and only ever widen, each end
        self.min = min(self.min, lowest)
        self.max = max(self.max, highest)
        # restore the flag
        self.dirty = marked
        # report the move
        return True

    def _envelope(self) -> tuple:
        """
        Report the span of my picks
        """
        # my range is my span
        return (self.low, self.high)

    # constants
    tag = "range"


# end of file
