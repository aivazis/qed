# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import cmath
import qed

# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.isce2.int.phase"):
    """
    Make a visualization pipeline to display the phase of complex values
    """

    # user configurable state
    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"

    brightness = qed.protocols.controller(default=qed.controllers.value)
    brightness.doc = "the brightness"

    # interface
    def autotune(self, stats, **kwds):
        # chain up
        super().autotune(**kwds)

        # if i'm supposed to
        if self.phase.auto:
            # get π
            π = cmath.pi
            # extract the high phase
            high = stats[1][2]
            # round up to the next multiple of 2π
            max = 2 * π * (int(high / (2 * π)) + 1)
            # adjust my range
            self.phase.min = 0
            self.phase.low = 0
            self.phase.max = max
            self.phase.high = high

        # if i'm supposed to
        if self.brightness.auto:
            # adjust my brightness
            self.brightness.value = 0.5

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
        # all done
        return

    def eval(self, amplitude, phase):
        """
        Get the phase of the pixel
        """
        # easy enough
        return phase

    def project(self, pixel):
        """
        Compute the phase of a {pixel}
        """
        # get the value as angle in radians in [-π, π]
        # N.B.: the range interval is closed thanks to the peculiarities of {atan2}
        value = cmath.phase(pixel) / cmath.pi

        # project
        # in π radians
        yield value, "π radians"

        # transform to [0, 2π]
        if value < 0:
            # by adding a whole cycle to negative values
            value += 2

        # in degrees in [0, 360]
        yield 180 * value, "degrees"
        # in cycles, in [0,1]
        yield value / 2, "cycles"

        # all done
        return

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # unpack my configuration
        low = self.phase.low
        high = self.phase.high
        brightness = self.brightness.value

        # unpack the {tile} origin
        line, sample = origin
        # and its shape
        lines, samples = shape

        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape3D(shape=(lines, 1, samples))
        # the origin into a {pyre::grid::index_t}
        origin = qed.libpyre.grid.Index3D(index=(line, 1, sample))
        # and the zoom level into a {pyre::grid::index_t}
        stride = qed.libpyre.grid.Index3D(index=(2 ** zoom[0], 1, 2 ** zoom[1]))
        # look for the tile maker in {libqed}
        tileMaker = qed.libqed.isce2.unwrapped.channels.phase
        # and ask it to make a tile
        tile = tileMaker(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            low=low,
            high=high,
            brightness=brightness,
            **kwds
        )
        # and return it
        return tile

    # constants
    tag = "phase"


# end of file
