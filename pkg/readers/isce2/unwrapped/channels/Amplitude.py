# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Amplitude(Channel, family="qed.channels.isce2.unw.amplitude"):
    """
    Make a visualization pipeline to display the amplitude of complex values
    """

    # configurable state
    scale = qed.protocols.controller(default=qed.controllers.value)
    scale.doc = "the overall amplitude scaling"
    scale.quantity = "scale"

    exponent = qed.protocols.controller(default=qed.controllers.value)
    exponent.doc = "the amplitude exponent"
    exponent.quantity = "exponent"

    # interface
    def autotune(self, stats=None, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super().autotune(**kwds)
        # my statistics are a record per interleaved band; a product nobody has measured
        # yet arrives without them, and there is nothing to index into
        if stats is None:
            # so leave my controllers at their configured values
            return

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

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the amplitude band, through a power law,
        painted gray
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the signal out of the amplitude band
        self.head(recipe=recipe)
        # the power law
        recipe.factory(name="power", protocol=qed.viz.filter, pin=qed.viz.filters.power())
        recipe.product(name="brightnesses")
        recipe.bind(factory="power", slot="signal", product="signal")
        recipe.bind(factory="power", slot="power", product="brightnesses")
        # and paint it gray
        self.paint(recipe=recipe, data="brightnesses")
        # hand it off
        return recipe

    def settings(self) -> dict:
        """
        The settings my controllers impose on the factories of my recipe
        """
        # the power law, measured against my mean amplitude
        power = {"mean": self.mean, "scale": self.scale.value, "exponent": self.exponent.value}
        # assemble
        return {"power": power}

    def iterators(self, source, origin, shape, stride, **kwds):
        """
        Render the tile of {source} at {origin}+{shape}, at the given {stride}, with the fused
        iterators
        """
        # lift the tile into the layout, anchored at the amplitude band
        origin, shape, stride = self.layout(origin=origin, shape=shape, stride=stride, band=0)
        # look for the tile maker in {libqed}
        tileMaker = qed.libqed.isce2.unwrapped.channels.amplitude
        # ask it to make a tile and return it
        return tileMaker(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            mean=self.mean,
            scale=self.scale.value,
            exponent=self.exponent.value,
            **kwds,
        )

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the reference amplitude my power law divides by; it comes from a measurement, so
        # until one arrives it is the neutral value rather than a zero that would divide
        self.mean = 1
        # all done
        return

    # constants
    tag = "amplitude"
    # the amplitude band
    bands = {"raster": 0}


# end of file
