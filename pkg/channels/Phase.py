# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import cmath
import qed
# superclass
from .Channel import Channel
# my controllers
from .LinearRange import LinearRange
from .Value import Value


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.phase"):
   """
   Make a visualization pipeline to display the phase of complex values
   """


   # user configurable state
   phase = qed.protocols.controller(default=LinearRange)
   phase.doc = "the manager of the range of values to render"

   brightness = qed.protocols.controller(default=Value)
   brightness.doc = "the brightness"

   saturation = qed.protocols.controller(default=Value)
   saturation.doc = "the saturation"


   # interface
   def autotune(self, **kwds):
      # chain up
      super().autotune(**kwds)
      # adjust my range
      self.phase.min = 0
      self.phase.low = 0
      self.phase.max = 1
      self.phase.high = 1
      # my brightness
      self.brightness.value = 1
      # and my saturation
      self.saturation.value = 1
      # all done
      return


   def controllers(self, **kwds):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers(**kwds)
      # my phase
      yield self.phase, self.pyre_trait(alias="phase")
      # my brightness
      yield self.brightness, self.pyre_trait(alias="brightness")
      # and my saturation
      yield self.saturation, self.pyre_trait(alias="saturation")
      # all done
      return


   def eval(self, pixel):
      """
      Get the {pixel} value
      """
      # easy enough
      return cmath.phase(pixel)


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
      # unpack my configuration
      low = self.phase.low
      high = self.phase.high
      saturation = self.saturation.value
      brightness = self.brightness.value
      # add my configuration and chain up
      return super().tile(low=low, high=high, saturation=saturation, brightness=brightness, **kwds)


   # constants
   tag = "phase"


# end of file
