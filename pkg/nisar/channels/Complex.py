# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.nisar.channels.complex"):
   """
   Make a visualization pipeline to display complex values
   """


   # constants
   tag = "complex"


   # user configurable state
   min = qed.properties.float(default=0)
   min.doc = "the minimum value; anything below is underflow"

   max = qed.properties.float(default=1000)
   max.doc = "the maximum value; anything above is overflow"

   saturation = qed.properties.float(default=1.0)
   saturation.doc = "the saturation"


   # interface
   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(min=self.min, max=self.max, saturation=self.saturation, **kwds)


# end of file
