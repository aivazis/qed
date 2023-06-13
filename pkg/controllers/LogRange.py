# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


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
    low = qed.properties.float(default=-1)
    low.doc = "the lowest value; anything below is underflow"

    high = qed.properties.float(default=3)
    high.doc = "the highest value; anything above is overflow"

    min = qed.properties.float(default=-2)
    min.doc = "the smallest possible value"

    max = qed.properties.float(default=4)
    max.doc = "the largest possible value"

    # interface
    def autotune(self, stats, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super().autotune(stats=stats, **kwds)

        # unpack the stats
        _, mean, high = stats

        # we want to be conservative, as this logic is only supposed to make sure that
        # the initial display is sensible; to this end, we leave both values at the low end
        # of the range at their default values

        # at the other end, use the gathered mean to set the {high} value
        # first, make sure the mean value won't cause problems
        mean = max(mean, 1)
        # same for the high value
        high = max(high, 1)
        # scale the mean up a bit to form the high value
        self.high = math.log10(4 * mean)
        # and set the max value to the next higher power of 10
        self.max = math.ceil(max(self.high, math.log10(high)))

        # all done
        return

    def updateRange(self, low, high):
        """
        Update my state with new values for the range
        """
        # update my state
        self.low = low
        self.high = high

        # and let the caller know
        return True

    # constants
    tag = "range"


# end of file
