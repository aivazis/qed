# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel

# the colormap that shows my codes
from ...GCOVPalette import GCOVPalette


# a channel for GCOV product masks
class GCOVMask(Channel, family="qed.channels.nisar.gcovmask"):
    """
    Make a visualization pipeline to display a GCOV product mask
    """

    # interface
    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # i don't have any controllers
        return []

    def recipe(self):
        """
        The pipeline that renders my tiles: the window of the mask, each code in its color
        """
        # make a recipe
        recipe = qed.flow.recipe()
        # cut the codes out of the mask
        self.head(recipe=recipe)
        # the colormap that knows them
        recipe.factory(name="palette", protocol=qed.viz.colormap, pin=GCOVPalette)
        # reads them
        recipe.bind(factory="palette", slot="mask", product="signal")
        # and its colors are encoded
        return self.encode(recipe=recipe, colormap="palette")

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # easy enough
        return pixel

    def project(self, pixel):
        """
        Compute the representation of a {pixel}
        """
        # only one rep
        yield pixel, ""
        # all done
        return

    # constants
    tag = "gcov"
    category = "masks"


# end of file
