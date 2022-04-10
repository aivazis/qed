# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Ranged import Ranged


# a channel for displaying complex values
class Complex(Ranged, family="qed.channels.complex"):
   """
   Make a visualization pipeline to display complex values
   """


   # constants
   tag = "complex"


   # user configurable state
   saturation = qed.properties.float(default=1.0)
   saturation.doc = "the saturation"


   # interface
   def controllers(self, **kwds):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers(**kwds)
      # all done
      return


   def tile(self, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # add my configuration and chain up
      return super().tile(saturation=self.saturation, **kwds)


   def project(self, pixel):
      """
      Represent a {pixel} as a complex number
      """
      # only one rep
      yield pixel, ""
      # all done
      return


# end of file
