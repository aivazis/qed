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
class Amplitude(Value, family="qed.channels.amplitude"):
    """
    A visualization pipeline fragment that renders the amplitude of a complex signal in gray
    scale: the amplitude is extracted, the values in a chosen interval are mapped onto [0,1], and
    painted gray

    The base channel contributes the encoder that generates the image tile that is sent to the
    client
    """

    # the selector that extracts the amplitude
    selector = qed.viz.selector()
    selector.default = qed.viz.selectors.amplitude
    selector.doc = "the selector that extracts the amplitude of each sample"

    # framework hooks
    def pyre_configured(self, **kwds):
        """
        Hook invoked after configuration is finished
        """
        # the normalizer reads the amplitude
        self.normalizer.signal = self.selector.amplitude
        # all done
        return super().pyre_configured(**kwds)


# end of file
