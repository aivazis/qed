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
   scale = qed.protocols.controller(default=qed.controllers.value)
   scale.doc = "the overall amplitude scaling"

   exponent = qed.protocols.controller(default=qed.controllers.value)
   exponent.doc = "the amplitude exponent"


   # interface
   def autotune(self, stats, **kwds):
      """
      Use the {stats} gathered on a data sample to adjust the range configuration
      """
      # chain up
      super().autotune(**kwds)

      # set my scale
      self.scale.value = 0.5
      # and my exponent
      self.exponent.value = 0.3
      # record the mean amplitude
      self.mean = stats[0][1]

      # all done
      return


   def controllers(self):
      """
      Generate the controllers that manipulate my state
      """
      # chain up
      yield from super().controllers()
      # my scale
      yield self.scale, self.pyre_trait(alias="scale")
      # and my exponent
      yield self.exponent, self.pyre_trait(alias="exponent")
      # all done
      return


   def eval(self, amplitude, phase):
      """
      Get the amplitude of the pixel
      """
      # easy enough
      return amplitude


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
      scale = self.scale.value
      exponent = self.exponent.value
      # and the mean amplitude
      mean = self.mean

      # unpack the {tile} origin
      line, sample = origin
      # and its shape
      lines, samples = shape

      # turn the shape into a {pyre::grid::shape_t}
      shape = qed.libpyre.grid.Shape3D(shape=(lines, 1, samples))
      # and the origin into a {pyre::grid::index_t}
      origin = qed.libpyre.grid.Index3D(index=(line, 0, sample))
      # look for the tile maker in {libqed}
      tileMaker = qed.libqed.isce2.unwrapped.channels.amplitude
      # and ask it to make a tile
      tile = tileMaker(source=source.data,
                       zoom=zoom, origin=origin, shape=shape,
                       mean=mean, scale=scale, exponent=exponent,
                       **kwds)
      # and return it
      return tile


   # metamethods
   def __init__(self, **kwds):
      # chain up
      super().__init__(**kwds)
      # the mean amplitude; set during auto tuning
      self.mean = 0
      # all done
      return


   # constants
   tag = "amplitude"


# end of file
