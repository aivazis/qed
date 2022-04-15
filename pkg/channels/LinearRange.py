# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# external
import math
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

   min = qed.properties.float(default=1.0e-3)
   min.doc = "the smallest possible value"

   max = qed.properties.float(default=1.0e+3)
   max.doc = "the largest possible value"


   # interface
   def autotune(self, stats, **kwds):
      """
      Use the {stats} gathered on a data sample to adjust the range configuration
      """
      # chain up
      super().autotune(stats=stats, **kwds)

      # unpack the stats
      _, mean, _ = stats

      # we want to be conservative, as this logic is only supposed to make sure that
      # the initial display is sensible
      self.high = 4 * mean
      # use the opposite for the low end
      self.low = -self.high

      # set the max value to the next higher power of 10
      self.max = 10**(math.ceil(math.log10(self.high)))
      # and the min to the opposite
      self.min = -self.max

      # all done
      return


   # constants
   tag = "range"


# end of file
