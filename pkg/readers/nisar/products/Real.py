# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .Product import Product


# a NISAR real data product
class Real(Product, family="qed.datasets.nisar.products.real"):
    """
    A real dataset
    """

    # public data
    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "float32"
    cell.doc = "the type of the dataset payload"

    # constants
    # the in-memory data layout of NISAR real data products
    datatype = qed.h5.memtypes.float32


# end of file
