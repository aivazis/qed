# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# raw dataset, i.e. a dataset in binary file with no metadata
class Raw(qed.flow.product, family="qed.datasets.raw", implements=qed.protocols.dataset):
    """
    A raw dataset
    """


    # public data
    # the payload; leave untyped for now
    data = qed.properties.object()
    data.default = None
    data.doc = "the memory payload"

    # the data layout
    cell = qed.protocols.datatype()
    cell.default = None
    cell.doc = "the type of the dataset payload"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = 0,0
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    selector = qed.properties.kv()
    selector.default = {}
    selector.doc = "a key/value map that identifies the dataset to a reader"


# end of file
