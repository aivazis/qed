# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import math
import qed

# superclass
from .Channel import Channel

# recolors the cells my mask flags
from ...GUNWScreen import GUNWScreen


# a channel for displaying the phase of complex values
class UnwrappedPhaseMasked(Channel, family="qed.channels.nisar.unwrappedPhaseMasked"):
    """
    Make a visualization pipeline to display the phase of complex values
    """

    # user configurable state
    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"
    phase.quantity = "phase"

    brightness = qed.protocols.controller(default=qed.controllers.value)
    brightness.doc = "the brightness"
    brightness.quantity = "brightness"

    # interface
    def autotune(self, **kwds):
        # chain up
        super().autotune(**kwds)
        # notify my range
        self.phase.autotune(**kwds)
        # if my brightness needs autotuning
        if self.brightness.auto:
            # adjust it to the middle of the scale
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

    def eval(self, phase):
        """
        Get the phase of the pixel
        """
        # easy enough
        return phase

    def project(self, pixel):
        """
        Compute the phase of a {pixel}
        """
        # get π
        π = math.pi
        # get the value of the phase, in radians per the spec
        value = pixel
        # project to π radians
        value = value / π

        # project
        # in π radians
        yield value, "π radians"
        # in degrees in [0, 360]
        yield 180 * value, "degrees"
        # in cycles, in [0,1]
        yield value / 2, "cycles"

        # all done
        return

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the raster, mapped onto the hues, at a
        constant luminosity, with the cells the mask flags and the cells with no data
        recolored
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the signal out of the raster
        self.head(recipe=recipe)
        # place the phase in its interval
        recipe.factory(name="normalizer", protocol=qed.viz.normalizer)
        # map it onto hues that span a full turn
        recipe.factory(
            name="hue",
            protocol=qed.viz.filter,
            pin=qed.viz.filters.affine(),
            settings={"interval": (0, 2 * math.pi)},
        )
        # a constant luminosity
        recipe.factory(name="brightness", protocol=qed.viz.filter, pin=qed.viz.filters.constant())
        # the products
        for name in ("phases", "hues", "luminosities"):
            # one at a time
            recipe.product(name=name)
        # the bindings
        recipe.bind(factory="normalizer", slot="signal", product="signal")
        recipe.bind(factory="normalizer", slot="normalized", product="phases")
        recipe.bind(factory="hue", slot="signal", product="phases")
        recipe.bind(factory="hue", slot="affine", product="hues")
        recipe.bind(factory="brightness", slot="tile", product="luminosities")
        # and paint
        self.light(recipe=recipe, hues="hues", luminosity="luminosities")
        # hand it off
        return recipe

    def settings(self) -> dict:
        """
        The settings my controllers impose on the factories of my recipe
        """
        # assemble
        return {
            # the range of the phase
            "normalizer": {"interval": (self.phase.low, self.phase.high)},
            # and the brightness
            "brightness": {"value": self.brightness.value},
        }

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # unpack my configuration
        low = self.phase.low
        high = self.phase.high
        brightness = self.brightness.value
        # make a tile and return it
        return super().tile(min=low, max=high, brightness=brightness, **kwds)

    # constants
    # my kernel builds its own pipeline, so it can be told what the product
    # declared and paint the two kinds of absence apart
    absence = True
    # recolors the cells my mask flags
    screenClass = GUNWScreen
    tag = "unwrappedMasked"
    category = "real"


# end of file
