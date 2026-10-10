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
class Amplitude(Channel, family="qed.channels.isce2.int.amplitude"):
    """
    Make a visualization pipeline to display the amplitude of complex values
    """

    # configurable state
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the range of values to render"
    amplitude.quantity = "amplitude"

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the amplitude configuration
        """
        # chain up
        super().autotune(**kwds)
        # notify my amplitude
        self.amplitude.autotune(**kwds)
        # all done
        return

    def controllers(self):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers()
        # my amplitude
        yield self.amplitude, self.pyre_trait(alias="amplitude")
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
        Compute the amplitude of a {pixel}
        """
        # only one choice
        yield abs(pixel), ""
        # and done
        return

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the raster, its amplitude normalized
        and painted gray
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the signal out of the raster
        self.head(recipe=recipe)
        # compute its amplitude
        recipe.factory(
            name="amplitude", protocol=qed.viz.operator, pin=qed.viz.operators.amplitude()
        )
        recipe.product(name="magnitude")
        recipe.bind(factory="amplitude", slot="signal", product="signal")
        recipe.bind(factory="amplitude", slot="amplitude", product="magnitude")
        # and paint it gray
        self.gray(recipe=recipe, signal="magnitude")
        # hand it off
        return recipe

    def settings(self) -> dict:
        """
        The settings my controllers impose on the factories of my recipe
        """
        # my range, which my controller keeps in decades
        interval = (10**self.amplitude.low, 10**self.amplitude.high)
        # goes to the normalizer
        return {"normalizer": {"interval": interval}}

    def tile(self, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # get my configuration
        low = 10**self.amplitude.low
        high = 10**self.amplitude.high
        # add my configuration and chain up
        return super().tile(min=low, max=high, **kwds)

    # constants
    tag = "amplitude"

    # the description of the pipeline
    @classmethod
    def description(cls):
        """
        The flow that describes what i compute
        """
        # the amplitude, painted gray
        return qed.channels.amplitude


# end of file
