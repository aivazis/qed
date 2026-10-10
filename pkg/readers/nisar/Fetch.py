# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the slicer that reads windows of the rasters of nisar products
class Fetch(qed.flow.factory, family="qed.readers.nisar.fetch", implements=qed.viz.slicer):
    """
    Read a window of a raster of a nisar product, a dataset or a level of its pyramid, into a
    tile: the cell at {row, column} of the tile is the cell of the raster at
    {(origin + {row, column}) * stride}, so {origin} is counted in strides; only the cells the
    window samples are read
    """

    # user configurable state
    origin = qed.properties.tuple(schema=qed.properties.int(), default=(0, 0))
    origin.doc = "the location of the window, counted in strides, one per axis"

    stride = qed.properties.tuple(schema=qed.properties.int(), default=(1, 1))
    stride.doc = "the distance between the cells of the raster the window samples, one per axis"

    # the input
    source = qed.viz.raster.input()
    source.doc = "the raster to read the tile out of"

    # the output
    slice = qed.viz.tile.output()
    slice.doc = "the tile"

    # the c++ templates whose instantiations do my work, when a recipe is staged
    pyre_engines = ("qed::nisar::flow::fetch_t",)


# end of file
