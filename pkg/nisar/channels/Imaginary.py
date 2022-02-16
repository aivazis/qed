# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying the imaginary part of complex values
class Imaginary(Channel, family="qed.nisar.channels.imaginary"):
   """
   Make a visualization pipeline to display the imaginary part of complex values
   """


   # constants
   tag = "imaginary"


   # user configurable state
   min = qed.properties.float(default=-1000.0)
   min.doc = "the minimum value; anything below is underflow"

   max = qed.properties.float(default=1000.0)
   max.doc = "the maximum value; anything above is overflow"


   # interface
   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(min=self.min, max=self.max, **kwds)


# end of file
