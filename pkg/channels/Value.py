# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# channels are visualization pipeline fragments, i.e. partial flows
class Value(Channel, family="qed.channels.value"):
    """
    A visualization pipeline fragment that renders a real valued signal in gray scale: the values
    in a chosen interval are mapped onto [0,1] and painted gray

    The base channel contributes the encoder that generates the image tile that is sent to the
    client
    """

    # the filter that maps the interval of interest onto [0,1]
    normalizer = qed.viz.filter()
    normalizer.default = qed.viz.filters.parametric
    normalizer.doc = "the filter that maps the interval of interest onto [0,1]"

    # the colormap
    gray = qed.viz.colormap()
    gray.default = qed.viz.colormaps.gray
    gray.doc = "the colormap that turns the normalized values into gray"

    # framework hooks
    def pyre_configured(self, **kwds):
        """
        Hook invoked after configuration is finished
        """
        # the colormap paints the normalized signal
        self.gray.data = self.normalizer.parametric
        # the encoder paints the red channel of its image with the red of the colormap
        self.codec.red = self.gray.red
        # the green with its green
        self.codec.green = self.gray.green
        # and the blue with its blue
        self.codec.blue = self.gray.blue
        # all done
        return super().pyre_configured(**kwds)


# end of file
