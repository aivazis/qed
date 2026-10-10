# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# recolor the cells a GCOV mask flags
class GCOVScreen(
    qed.flow.factory, family="qed.readers.nisar.gcovScreen", implements=qed.viz.filter
):
    """
    Recolor the cells a GCOV mask flags: faint brick red outside the acquisition, black where the
    sample is invalid
    """

    # the inputs
    mask = qed.viz.tile.input()
    mask.doc = "the codes of the mask"

    red = qed.viz.protocols.channel.input()
    red.doc = "the red channel of the colors of the cells"

    green = qed.viz.protocols.channel.input()
    green.doc = "the green channel of the colors of the cells"

    blue = qed.viz.protocols.channel.input()
    blue.doc = "the blue channel of the colors of the cells"

    # the outputs
    paintedRed = qed.viz.protocols.channel.output()
    paintedRed.doc = "the red channel, with the cells the mask flags recolored"

    paintedGreen = qed.viz.protocols.channel.output()
    paintedGreen.doc = "the green channel, with the cells the mask flags recolored"

    paintedBlue = qed.viz.protocols.channel.output()
    paintedBlue.doc = "the blue channel, with the cells the mask flags recolored"

    # the c++ templates whose instantiations do my work, when a recipe is staged
    pyre_engines = ("qed::nisar::flow::gcov_screen_t",)


# end of file
