# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import cmath
import qed
# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.phase"):
   """
   Make a visualization pipeline to display the phase of complex values
   """


   # constants
   tag = "phase"


   # user configurable state
   brightness = qed.properties.float(default=1.0)
   brightness.doc = "the brightness"

   saturation = qed.properties.float(default=1.0)
   saturation.doc = "the saturation"


   # interface
   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(saturation=self.saturation, brightness=self.brightness, **kwds)


   def rep(self, pixel):
      """
      Build a representation of {pixel}
      """
      # easy
      return f"{cmath.phase(pixel):.3g}"


# end of file
