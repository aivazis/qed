# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# my superclass
from .Producer import Producer
# my product specs
from .Dataset import Dataset
from .Layout import Layout


# the product payload
class Reader(Producer, family="qed.factories.readers"):
    """
    A dataset factory
    """


    # public data
    # the payload
    data = Dataset.output()
    data.doc = "the memory payload"

    # its metadata; more specialized classes can decide whether this is input or output
    # depending on how self describing the data source is
    layout = Layout()
    layout.doc = "the dataset layout"


# end of file
