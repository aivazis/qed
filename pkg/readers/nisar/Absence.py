# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# recolor the cells with no data
class Absence(qed.flow.factory, family="qed.readers.nisar.absence", implements=qed.viz.filter):
    """
    Recolor the cells with no data: a cell whose magnitude is the {fill} the product declared
    turns faint brick red, a nan the product did not declare gets a color of its own, and every
    other cell keeps its color
    """

    # user configurable state
    fill = qed.properties.float(default=float("nan"))
    fill.doc = "the magnitude of the value the product declared it writes where it has no data"

    # the inputs
    data = qed.viz.tile.input()
    data.doc = "the cells of the raster"

    red = qed.viz.protocols.channel.input()
    red.doc = "the red channel of the colors of the cells"

    green = qed.viz.protocols.channel.input()
    green.doc = "the green channel of the colors of the cells"

    blue = qed.viz.protocols.channel.input()
    blue.doc = "the blue channel of the colors of the cells"

    # the outputs
    paintedRed = qed.viz.protocols.channel.output()
    paintedRed.doc = "the red channel, with the cells with no data recolored"

    paintedGreen = qed.viz.protocols.channel.output()
    paintedGreen.doc = "the green channel, with the cells with no data recolored"

    paintedBlue = qed.viz.protocols.channel.output()
    paintedBlue.doc = "the blue channel, with the cells with no data recolored"

    # the c++ templates whose instantiations do my work, when a recipe is staged
    pyre_engines = ("qed::nisar::flow::absence_t",)


# end of file
