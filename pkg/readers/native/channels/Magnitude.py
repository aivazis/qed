# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying the absolute value of real values
class Magnitude(Channel, family="qed.channels.native.abs"):
    """
    Make a visualization pipeline to display the magnitude of real values
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
        return abs(pixel)

    def project(self, pixel):
        """
        Compute the real part of a {pixel}
        """
        # only one rep
        yield abs(pixel), ""
        # all done
        return

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # add my configuration and chain up
        return super().tile(min=self.range.low, max=self.range.high, **kwds)

    def gdal(self, source, shape, low, high):
        """
        Render a tile in a numpy array
        """
        # look for the tile maker in {libqed}
        pipeline = qed.libqed.native.channels.abs
        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape2D(shape=shape)
        # and invoke it
        return pipeline(source=source, shape=shape, low=low, high=high)

    # constants
    tag = "abs"


# end of file
