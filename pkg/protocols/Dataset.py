# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# support
import qed
# my superclass
from .Specification import Specification
# my parts
from .Datatype import Datatype


# the product payload
class Dataset(Specification, family="qed.datasets"):
    """
    A dataset provides access to the actual data
    """


    # public data
    # the payload; leave untyped for now
    data = qed.properties.object()
    data.doc = "the memory payload"

    # the data layout
    cell = Datatype()
    cell.doc = "the type of the dataset payload"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the shape of the dataset"


# end of file
