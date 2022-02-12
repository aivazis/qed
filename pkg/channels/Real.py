# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying the real part of complex values
class Real(Channel, family="qed.channels.real"):
   """
   Make a visualization pipeline to display the real part of complex values
   """


   # constants
   tag = "real"


   # interface
   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(min=-1000, max=1000, **kwds)


# end of file
