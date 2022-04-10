# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Ranged import Ranged


# a channel for displaying the amplitude of complex values
class Amplitude(Ranged, family="qed.channels.amplitude"):
   """
   Make a visualization pipeline to display the amplitude of complex values
   """


   # constants
   tag = "amplitude"


   # interface
   def project(self, pixel):
      """
      Compute the amplitude of a {pixel}
      """
      # only one choice
      yield abs(pixel), ""
      # and done
      return


# end of file
