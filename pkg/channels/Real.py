# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying the real part of complex values
class Real(Channel, family="qed.channels.real"):
   """
   Make a visualization pipeline to display the real part of complex values
   """


   # constants
   tag = "real"


   # user configurable state
   min = qed.properties.float(default=-1000.0)
   min.doc = "the minimum value; anything below is underflow"

   max = qed.properties.float(default=1000.0)
   max.doc = "the maximum value; anything above is overflow"


   # interface
   def tile(self, source, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # get my range
      low = self.min
      high = self.max
      # if either is uninitialized
      if low is None or high is None:
         # extract from the dataset
         low, mean, high = source.stats()
         # adjust
         high = min(high, 4*mean)
         low = -high
         # and remember for next time
         self.min = low
         self.max = high

      # add my configuration and chain up
      return super().tile(source=source, min=low, max=high, **kwds)


   def rep(self, pixel):
      """
      Build a representation of {pixel}
      """
      # easy
      return f"{pixel.real:.3g}"


# end of file
