# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import cmath

# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.isce2.unw.complex"):
    """
    Make a visualization pipeline to display complex values
    """

    # configurable state
    scale = qed.protocols.controller(default=qed.controllers.value)
    scale.doc = "the overall amplitude scaling"
    scale.quantity = "scale"

    exponent = qed.protocols.controller(default=qed.controllers.value)
    exponent.doc = "the amplitude exponent"
    exponent.quantity = "exponent"

    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"
    phase.quantity = "phase"

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

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the phase band mapped onto the hues,
        with the window of the amplitude band through a power law as the luminosity
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the amplitudes out of their band
        self.head(
            recipe=recipe, raster="amplitude.raster", signal="amplitudes", slicer="amplitude.slice"
        )
        # and the phases out of theirs
        self.head(recipe=recipe, raster="phase.raster", signal="phase", slicer="phase.slice")
        # the power law
        recipe.factory(name="power", protocol=qed.viz.filter, pin=qed.viz.filters.power())
        # place the phase in its interval
        recipe.factory(name="normalizer", protocol=qed.viz.normalizer)
        # map it onto hues that span a full turn
        recipe.factory(
            name="hue",
            protocol=qed.viz.filter,
            pin=qed.viz.filters.affine(),
            settings={"interval": (0, 2 * cmath.pi)},
        )
        # the products
        for name in ("luminosities", "phases", "hues"):
            # one at a time
            recipe.product(name=name)
        # the bindings
        recipe.bind(factory="power", slot="signal", product="amplitudes")
        recipe.bind(factory="power", slot="power", product="luminosities")
        recipe.bind(factory="normalizer", slot="signal", product="phase")
        recipe.bind(factory="normalizer", slot="normalized", product="phases")
        recipe.bind(factory="hue", slot="signal", product="phases")
        recipe.bind(factory="hue", slot="affine", product="hues")
        # and paint
        self.light(recipe=recipe, hues="hues", luminosity="luminosities")
        # hand it off
        return recipe

    def settings(self) -> dict:
        """
        The settings my controllers impose on the factories of my recipe
        """
        # the power law, measured against my mean amplitude
        power = {"mean": self.mean, "scale": self.scale.value, "exponent": self.exponent.value}
        # assemble
        return {
            # the power law
            "power": power,
            # and the range of the phase
            "normalizer": {"interval": (self.phase.low, self.phase.high)},
        }

    def iterators(self, source, origin, shape, stride, **kwds):
        """
        Render the tile of {source} at {origin}+{shape}, at the given {stride}, with the fused
        iterators
        """
        # lift the tile into the layout, anchored at the leading band
        origin, shape, stride = self.layout(origin=origin, shape=shape, stride=stride, band=0)
        # look for the tile maker in {libqed}
        tileMaker = qed.libqed.isce2.unwrapped.channels.complex
        # ask it to make a tile and return it
        return tileMaker(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            mean=self.mean,
            scale=self.scale.value,
            exponent=self.exponent.value,
            minPhase=self.phase.low,
            maxPhase=self.phase.high,
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
    tag = "complex"
    # the amplitude and phase bands
    bands = {"amplitude.raster": 0, "phase.raster": 1}


# end of file
