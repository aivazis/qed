# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Ranged import Ranged


# a channel for displaying the imaginary part of complex values
class Imaginary(Ranged, family="qed.channels.imaginary"):
   """
   Make a visualization pipeline to display the imaginary part of complex values
   """


   # constants
   tag = "imaginary"


   # user configurable state
   min = qed.properties.float(default=-1.0e3)
   min.doc = "the minimum value; anything below is underflow"

   max = qed.properties.float(default=1.0e3)
   max.doc = "the maximum value; anything above is overflow"


   # interface
   def project(self, pixel):
      """
      Compute the imaginary part of a {pixel}
      """
      # easy
      yield pixel.imag, ""
      # all done
      return


# end of file
