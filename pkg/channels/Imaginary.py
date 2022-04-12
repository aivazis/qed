# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel
# mixin
from .LinearRange import LinearRange


# a channel for displaying the imaginary part of complex values
class Imaginary(LinearRange, Channel, family="qed.channels.imaginary"):
   """
   Make a visualization pipeline to display the imaginary part of complex values
   """


   # constants
   tag = "imaginary"


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
