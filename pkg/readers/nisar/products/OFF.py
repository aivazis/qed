# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# superclass
from .Product import Product


# a NISAR offsets data product
class OFF(Product, family="qed.datasets.nisar.products.off"):
    """
    An OFF dataset
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "real32"
    cell.doc = "the type of the dataset payload"

    # constants
    # the in-memory data layout of NISAR complex data products
    datatype = qed.h5.memtypes.float32


# end of file
