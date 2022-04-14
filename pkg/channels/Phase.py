# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import cmath
import qed
# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.phase"):
   """
   Make a visualization pipeline to display the phase of complex values
   """


   # user configurable state
   brightness = qed.properties.float(default=1.0)
   brightness.doc = "the brightness"

   saturation = qed.properties.float(default=1.0)
   saturation.doc = "the saturation"


   # interface
   def controllers(self, **kwds):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers(**kwds)
      # my brightness
      # and my saturation
      # all done
      return


   def project(self, pixel):
      """
      Compute the phase of a {pixel}
      """
      # get the value as angle in radians in [-π, π]
      # N.B.: the range interval is closed thanks to the peculiarities of {atan2}
      value = cmath.phase(pixel) / cmath.pi

      # project
      # in π radians
      yield  value, "π radians"

      # transform to [0, 2π]
      if value < 0:
         # by adding a whole cycle to negative values
         value += 2

      # in degrees in [0, 360]
      yield 180*value, "degrees"
      # in cycles, in [0,1]
      yield value/2, "cycles"

      # all done
      return


   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(saturation=self.saturation, brightness=self.brightness, **kwds)


   # constants
   tag = "phase"


# end of file
