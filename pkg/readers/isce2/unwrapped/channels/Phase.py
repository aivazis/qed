# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import cmath
import qed

# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.isce2.unw.phase"):
    """
    Make a visualization pipeline to display the phase of complex values
    """

    # user configurable state
    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"
    phase.quantity = "phase"

    brightness = qed.protocols.controller(default=qed.controllers.value)
    brightness.doc = "the brightness"

    # interface
    def autotune(self, stats=None, **kwds):
        # chain up
        super().autotune(**kwds)
        # my statistics are a record per interleaved band; a product nobody has measured
        # yet arrives without them, and there is nothing to index into
        if stats is None:
            # so leave my controllers at their configured values
            return
        # notify my range, which reads the band that carries the phase
        self.phase.autotune(stats=stats[1], **kwds)
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

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the phase band, mapped onto the hues,
        at a constant luminosity
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the signal out of the phase band
        self.head(recipe=recipe)
        # place the phase in its interval
        recipe.factory(name="normalizer", protocol=qed.viz.normalizer)
        # map it onto hues that span a full turn
        recipe.factory(
            name="hue",
            protocol=qed.viz.filter,
            pin=qed.viz.filters.affine(),
            settings={"interval": (0, 2 * cmath.pi)},
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

    def iterators(self, source, origin, shape, stride, **kwds):
        """
        Render the tile of {source} at {origin}+{shape}, at the given {stride}, with the fused
        iterators
        """
        # lift the tile into the layout, anchored at the phase band
        origin, shape, stride = self.layout(origin=origin, shape=shape, stride=stride, band=1)
        # look for the tile maker in {libqed}
        tileMaker = qed.libqed.isce2.unwrapped.channels.phase
        # ask it to make a tile and return it
        return tileMaker(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            low=self.phase.low,
            high=self.phase.high,
            brightness=self.brightness.value,
            **kwds,
        )

    # constants
    tag = "phase"
    # the phase band
    bands = {"raster": 1}


# end of file
