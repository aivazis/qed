# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# my superclass
from .Producer import Producer

# my product specs
from .Dataset import Dataset

# local traits
from . import properties


# the product payload
class Reader(Producer, family="qed.readers"):
    """
    A dataset factory
    """

    # public data
    uri = qed.properties.uri()
    uri.doc = "the uri of the data source"

    selectors = properties.selectors()
    selectors.doc = "a map of selector names to their allowed values"

    datasets = qed.properties.list(schema=Dataset())
    datasets.doc = "the list of data sets provided by the reader"

    # requirements
    @qed.provides
    def open(self):
        """
        Establish first contact with the data source: open the file, discover the datasets,
        and derive the selector availability

        Construction is passive, so a reader can be built, cataloged, and shipped without
        touching its file; whoever needs the data initiates the contact, and repeated calls
        are harmless
        """


# end of file
