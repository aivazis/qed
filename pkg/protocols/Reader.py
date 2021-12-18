# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# support
import qed
# my superclass
from .Producer import Producer
# my product specs
from .Dataset import Dataset


# the product payload
class Reader(Producer, family="qed.readers"):
    """
    A dataset factory
    """


    # public data
    uri = qed.properties.path()
    uri.doc = "the uri of the data source"

    datasets = qed.properties.list(schema=Dataset())
    datasets.doc = "the list of data sets provided by the reader"


# end of file
