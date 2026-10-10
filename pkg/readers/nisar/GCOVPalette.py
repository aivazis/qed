# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the colormap that shows the mask of a GCOV product by itself
class GCOVPalette(
    qed.flow.factory, family="qed.readers.nisar.gcovPalette", implements=qed.viz.colormap
):
    """
    Color every code of the mask of a GCOV product the way its mask channel draws it
    """

    # the input
    mask = qed.viz.tile.input()
    mask.doc = "the codes of the mask"

    # the outputs
    red = qed.viz.protocols.channel.output()
    red.doc = "the red channel"

    green = qed.viz.protocols.channel.output()
    green.doc = "the green channel"

    blue = qed.viz.protocols.channel.output()
    blue.doc = "the blue channel"

    # the c++ templates whose instantiations do my work, when a recipe is staged
    pyre_engines = ("qed::nisar::flow::gcov_palette_t",)


# end of file
