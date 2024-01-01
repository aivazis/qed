# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Product import Product


# a NISAR SLC
class SLC(Product, family="qed.datasets.nisar.products.slc"):
    """
    An SLC dataset
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"

    # constants
    # the in-memory data layout of NISAR complex data products
    datatype = qed.h5.memtypes.complex64


# end of file
