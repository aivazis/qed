# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel
# my parts
from .LogRange import LogRange


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.complex"):
   """
   Make a visualization pipeline to display complex values
   """


   # configurable state
   range = qed.protocols.controller(default=LogRange)
   range.doc = "the manager of the range of values to render"

   saturation = qed.properties.float(default=1.0)
   saturation.doc = "the saturation"


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
      yield self.range
      # and my saturation
      # all done
      return


   def project(self, pixel):
      """
      Represent a {pixel} as a complex number
      """
      # only one rep
      yield pixel, ""
      # all done
      return


   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # get my configuration
      low = 10**self.range.low
      high = 10**self.range.high
      saturation = self.saturation
      # add my configuration and chain up
      return super().tile(min=low, max=high, saturation=saturation, **kwds)


   # constants
   tag = "complex"


# end of file
