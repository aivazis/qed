# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# external
import math
# support
import qed


# a mixin for a channel with rel values in a linear range
class LinearRange(qed.component, family="qed.channels.linearrange"):
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


   def controllers(self, **kwds):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers(**kwds)

      # a controller for my brightness
      yield {
         "id": f"{self.pyre_name}.brightness",
         "uuid": self.pyre_id,
         "controller": "linearrange",
         "slot": "signal",
         "min": self.min,
         "max": self.max,
         "low": self.low,
         "high": self.high,
      }

      # all done
      return


   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(min=self.low, max=self.high, **kwds)


# end of file
