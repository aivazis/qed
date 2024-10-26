# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# my superclass
from .Specification import Specification

# my parts
from .Channel import Channel
from .Datatype import Datatype


# the product payload
class Dataset(Specification, family="qed.datasets"):
    """
    A dataset provides access to the actual data
    """

    # public data
    cell = Datatype()
    cell.doc = "the type of the dataset payload"

    channels = qed.properties.dict(schema=Channel())
    channels.doc = "the table of channels supported by this dataset"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the shape of the dataset"

    selector = qed.properties.kv()
    selector.doc = "a key/value map that identifies the dataset to a reader"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.doc = "the preferred shape of dataset subsets"


# end of file
