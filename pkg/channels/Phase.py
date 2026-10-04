# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .Channel import Channel


# channels are visualization pipeline fragments, i.e. partial flows
class Phase(Channel, family="qed.channels.phase"):
    """
    A visualization pipeline fragment that is suitable for rendering the phase of data tiles

    The base channel contributes the encoder that generates the image tile that is sent to the
    client
    """

    # the colormap
    hsb = qed.viz.colormap()
    hsb.default = qed.viz.colormaps.hsb
    hsb.doc = "the HSB colormap that turns phase into color"

    # framework hooks
    def pyre_configured(self, **kwds):
        """
        Hook invoked after configuration is finished
        """
        # the encoder paints the red channel of its image with the red of the colormap
        self.codec.red = self.hsb.red
        # the green with its green
        self.codec.green = self.hsb.green
        # and the blue with its blue
        self.codec.blue = self.hsb.blue
        # all done
        return super().pyre_configured(**kwds)


# end of file
