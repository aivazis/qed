# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the selector that picks the dataset to look at
class Dataset(
    qed.flow.factory, family="qed.readers.selectors.dataset", implements=qed.viz.selector
):
    """
    Pick the dataset to look at among the ones a reader found in a file, and make its cells
    available as a raster
    """

    # the input
    datasets = qed.viz.protocols.datasets.input()
    datasets.doc = "the datasets a reader found"

    # the output
    raster = qed.viz.tile.output()
    raster.doc = "the cells of the dataset, shared rather than copied"


# end of file
