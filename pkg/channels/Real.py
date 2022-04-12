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


# a channel for displaying the real part of complex values
class Real(LinearRange, Channel, family="qed.channels.real"):
   """
   Make a visualization pipeline to display the real part of complex values
   """


   # constants
   tag = "real"


   # interface
   def project(self, pixel):
      """
      Compute the real part of a {pixel}
      """
      # only one rep
      yield pixel.real, ""
      # all done
      return


# end of file
