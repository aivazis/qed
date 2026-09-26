# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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
    channels.persistent = False

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the shape of the dataset"

    selector = qed.properties.kv()
    selector.doc = "a key/value map that identifies the dataset to a reader"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.doc = "the preferred shape of dataset subsets"

    # obligations
    @qed.provides
    def sample(self, zoom, origin, shape):
        """
        Collect a mergeable statistical sample of the tile at {origin}+{shape}, visiting exactly
        the cells the render at {zoom} sees, as the record {(count, min, mean, m2, max)} of their
        magnitudes; cells that hold no value are left out, and a tile of nothing but those
        yields the empty record, which merges into an accumulator without moving it
        """


# end of file
