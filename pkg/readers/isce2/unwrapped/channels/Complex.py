# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import cmath

# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.isce2.int.complex"):
    """
    Make a visualization pipeline to display complex values
    """

    # configurable state
    scale = qed.protocols.controller(default=qed.controllers.value)
    scale.doc = "the overall amplitude scaling"

    exponent = qed.protocols.controller(default=qed.controllers.value)
    exponent.doc = "the amplitude exponent"

    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"

    # interface
    def autotune(self, stats, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super().autotune(**kwds)

        # if i'm supposed to
        if self.scale.auto:
            # set my scale
            self.scale.value = 0.5
        # if i'm supposed to
        if self.exponent.auto:
            # adjust my exponent
            self.exponent.value = 0.3
        # record the mean amplitude
        self.mean = stats[0][1]

        # autotune the phase
        self.phase.autotune(stats=stats[1])

        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my scale
        yield self.scale, self.pyre_trait(alias="scale")
        # and my exponent
        yield self.exponent, self.pyre_trait(alias="exponent")
        # my phase
        yield self.phase, self.pyre_trait(alias="phase")
        # all done
        return

    def eval(self, amplitude, phase):
        """
        Get the amplitude of the pixel
        """
        # easy enough
        return cmath.rect(amplitude, phase)

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
        minPhase = self.phase.low
        maxPhase = self.phase.high
        # and the mean amplitude
        mean = self.mean

        # unpack the {tile} origin
        line, sample = origin
        # and its shape
        lines, samples = shape

        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape3D(shape=(lines, 1, samples))
        # the origin into a {pyre::grid::index_t}
        origin = qed.libpyre.grid.Index3D(index=(line, 0, sample))
        # and the zoom level into a {pyre::grid::index_t}
        stride = qed.libpyre.grid.Index3D(index=(2 ** zoom[0], 1, 2 ** zoom[1]))
        # look for the tile maker in {libqed}
        tileMaker = qed.libqed.isce2.unwrapped.channels.complex
        # and ask it to make a tile
        tile = tileMaker(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            mean=mean,
            scale=scale,
            exponent=exponent,
            minPhase=minPhase,
            maxPhase=maxPhase,
            **kwds
        )
        # and return it
        return tile

    # constants
    tag = "complex"


# end of file
