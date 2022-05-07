# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying the imaginary part of complex values
class Imaginary(Channel, family="qed.channels.isce2.int.imaginary"):
   """
   Make a visualization pipeline to display the imaginary part of complex values
   """


   # configurable state
   range = qed.protocols.controller(default=qed.controllers.linearRange)
   range.doc = "the manager of the range of values to render"


   # interface
   def autotune(self, **kwds):
      """
      Use the {stats} gathered on a data sample to adjust the range configuration
      """
      # chain up
      super().autotune(**kwds)
      # notify my range
      self.range.autotune(**kwds)
      # all done
      return


   def controllers(self, **kwds):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers(**kwds)
      # my range
      yield self.range, self.pyre_trait(alias="range")
      # all done
      return


   def eval(self, pixel):
      """
      Get the {pixel} value
      """
      # easy enough
      return pixel.imag


   def project(self, pixel):
      """
      Compute the imaginary part of a {pixel}
      """
      # easy
      yield pixel.imag, ""
      # all done
      return


   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(min=self.range.low, max=self.range.high, **kwds)


   # constants
   tag = "imaginary"


# end of file
