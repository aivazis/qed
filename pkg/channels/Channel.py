# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal


# channels are visualization pipeline fragments, i.e. partial flows
class Channel(qed.flow.workflow, family="qed.channels.channel"):
    """
    A visualization pipeline fragment that is suitable for rendering data tiles

    The base channel contributes the encoder that generates the image tile that is sent to the
    client
    """

    # products
    # expose the output node; everything else is internal, as far as clients are concerned
    # lean on the protocols for sensible defaults
    bmp = qed.viz.raster.output()
    bmp.doc = "the final rendered image of the channel"

    # factories
    codec = qed.viz.codec()
    codec.doc = "the encoder of the data tile as an image to be rendered by the client"

    # framework hooks
    def pyre_configured(self, **kwds):
        """
        Hook invoked after configuration is finished
        """
        # wire my output into the flow
        self.codec.bmp = self.bmp
        # all done
        return super().pyre_configured(**kwds)


# end of file
