# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import math

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
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the range of values to render"
    amplitude.quantity = "amplitude"

    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"
    phase.quantity = "phase"

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super().autotune(**kwds)
        # notify my amplitude
        self.amplitude.autotune(**kwds)
        # if i'm supposed to
        if self.phase.auto:
            # adjust my range
            self.phase.min = 0
            self.phase.low = 0
            self.phase.max = 1
            self.phase.high = 1
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my amplitude
        yield self.amplitude, self.pyre_trait(alias="amplitude")
        # my phase
        yield self.phase, self.pyre_trait(alias="phase")
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
        Represent a {pixel} as a complex number
        """
        # only one rep
        yield pixel, ""
        # all done
        return

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the raster, its phase as the hue and its
        normalized amplitude as the luminosity
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the signal out of the raster
        self.head(recipe=recipe)
        # compute its amplitude
        recipe.factory(
            name="amplitude", protocol=qed.viz.operator, pin=qed.viz.operators.amplitude()
        )
        # and normalize it
        recipe.factory(name="normalizer", protocol=qed.viz.normalizer)
        # the products
        recipe.product(name="magnitude")
        recipe.product(name="luminosities")
        # the bindings
        recipe.bind(factory="amplitude", slot="signal", product="signal")
        recipe.bind(factory="amplitude", slot="amplitude", product="magnitude")
        recipe.bind(factory="normalizer", slot="signal", product="magnitude")
        recipe.bind(factory="normalizer", slot="normalized", product="luminosities")
        # turn the phase into hues that span a full turn
        self.turn(recipe=recipe, signal="signal")
        recipe.node(name="hue").settings["interval"] = (0, 2 * math.pi)
        # and paint them, with the normalized amplitude as the luminosity
        self.light(recipe=recipe, hues="hues", luminosity="luminosities")
        # hand it off
        return recipe

    def settings(self) -> dict:
        """
        The settings my controllers impose on the factories of my recipe
        """
        # my amplitude, which my controller keeps in decades
        interval = (10**self.amplitude.low, 10**self.amplitude.high)
        # assemble
        return {
            # the range of the phase
            "cycle": {"interval": (self.phase.low, self.phase.high)},
            # and the range of the amplitude
            "normalizer": {"interval": interval},
        }

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # unpack my configuration
        low = 10**self.amplitude.low
        high = 10**self.amplitude.high
        lowPhase = self.phase.low
        highPhase = self.phase.high
        # add my configuration and chain up
        return super().tile(min=low, max=high, minPhase=lowPhase, maxPhase=highPhase, **kwds)

    # constants
    tag = "complex"


# end of file
