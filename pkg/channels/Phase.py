# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.phase"):
   """
   Make a visualization pipeline to display the phase of complex values
   """


   # constants
   tag = "phase"


   # interface
   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(saturation=1.0, brightness=0.75, **kwds)


# end of file
