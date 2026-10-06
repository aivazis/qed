# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Value import Value


# channels are visualization pipeline fragments, i.e. partial flows
class Imaginary(Value, family="qed.channels.imaginary"):
    """
    A visualization pipeline fragment that renders the imaginary part of a complex signal in gray
    scale: the imaginary part is extracted, the values in a chosen interval are mapped onto [0,1], and
    painted gray

    The base channel contributes the encoder that generates the image tile that is sent to the
    client
    """

    # the selector that extracts the imaginary part
    selector = qed.viz.selector()
    selector.default = qed.viz.selectors.imaginary
    selector.doc = "the selector that extracts the imaginary part of each sample"

    # framework hooks
    def pyre_configured(self, **kwds):
        """
        Hook invoked after configuration is finished
        """
        # the normalizer reads the imaginary part
        self.normalizer.signal = self.selector.imaginary
        # all done
        return super().pyre_configured(**kwds)


# end of file
