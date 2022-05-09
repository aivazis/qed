# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Amplitude(Channel, family="qed.channels.isce2.int.amplitude"):
   """
   Make a visualization pipeline to display the amplitude of complex values
   """


   # configurable state
   range = qed.protocols.controller(default=qed.controllers.logRange)
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


   def controllers(self):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers()
      # my range
      yield self.range, self.pyre_trait(alias="range")
      # all done
      return


   def eval(self, pixel):
      """
      Get the {pixel} value
      """
      # easy enough
      return pixel


   def project(self, pixel):
      """
      Compute the amplitude of a {pixel}
      """
      # only one choice
      yield pixel, ""
      # and done
      return


   def tile(self, source, zoom, origin, shape, **kwds):
      """
      Generate a tile of the given characteristics
      """
      # get my configuration
      low = 10**self.range.low
      high = 10**self.range.high

      # unpack the {tile} origin
      line, sample = origin
      # and its shape
      lines, samples = shape

      # turn the shape into a {pyre::grid::shape_t}
      shape = qed.libpyre.grid.Shape3D(shape=(lines, 1, samples))
      # and the origin into a {pyre::grid::index_t}
      origin = qed.libpyre.grid.Index3D(index=(line, 0, sample))
      # look for the tile maker in {libqed}
      tileMaker = qed.libqed.channels.value
      # and ask it to make a tile
      tile = tileMaker(source=source.data,
                       zoom=zoom, origin=origin, shape=shape, min=low, max=high, **kwds)
      # and return it
      return tile


   # constants
   tag = "amplitude"


# end of file
