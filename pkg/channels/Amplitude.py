# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Amplitude(Channel, family="qed.channels.amplitude"):
   """
   Make a visualization pipeline to display the amplitude of complex values
   """


   # constants
   tag = "amplitude"


   # interface
   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(min=0, max=1000, **kwds)


# end of file
