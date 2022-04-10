# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Ranged(Channel, family="qed.channels.ranged"):
   """
   A channel with a configurable parameter range
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
         "controller": "range",
         "slot": self.tag,
         "min": self.min,
         "max": self.max,
         "low": self.low,
         "high": self.high,
      }

      # all done
      return


   def tile(self, source, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # get my range
      low = self.low
      high = self.high
      # if either is uninitialized
      if low is None or high is None:
         # extract from the dataset
         low, mean, high = source.stats()
         # adjust
         high = min(high, 4*mean)
         # and remember for next time
         self.low = low
         self.high = high

      # add my configuration and chain up
      return super().tile(source=source, min=low, max=high, **kwds)


# end of file
