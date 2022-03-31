# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.complex"):
   """
   Make a visualization pipeline to display complex values
   """


   # constants
   tag = "complex"


   # user configurable state
   min = qed.properties.float(default=None)
   min.doc = "the minimum value; anything below is underflow"

   max = qed.properties.float(default=None)
   max.doc = "the maximum value; anything above is overflow"

   saturation = qed.properties.float(default=1.0)
   saturation.doc = "the saturation"


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
         # and remember for next time
         self.min = low
         self.max = high

      # add my configuration and chain up
      return super().tile(source=source,
                          min=low, max=high, saturation=self.saturation,
                         **kwds)


   def rep(self, pixel):
      """
      Build a representation of {pixel}
      """
      # easy
      return f"{pixel:.3g}"


# end of file
