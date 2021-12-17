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


# the dataset layout
class Layout(Specification, family="qed.products.layouts"):
    """
    The dataset metadata
    """


    # public data
    # individual metadata, used to assemble a default layout
    cell = Datatype()
    cell.doc = "the type of the dataset payload"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the shape of the dataset"


# end of file
