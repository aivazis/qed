# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# the basic reader for products in HDF5 format
class H5(qed.flow.factory, implements=qed.protocols.reader):
    """
    The base class for readers of HDF5 files
    """

    # user configurable state
    uri = qed.properties.uri(scheme="file")
    uri.doc = "the uri of the data source"

    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the list of data sets provided by the reader"

    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"

    pages = qed.properties.int()
    pages.default = None
    pages.doc = "the number of 4K pages in the aggregation cache"

    # metamethods
    def __init__(self, fapl=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # if the caller didn't provide an access property list
        if fapl is None:
            # make a default one
            fapl = qed.h5.libh5.FAPL()
        # get the number of pages to set aside for the page aggregator
        pages = self.pages
        # if it is non-trivial
        if pages:
            # form the cache size
            size = 4 * 1024 * pages
            # adjust the {fapl}
            fapl.setPageBufferSize(page=size, meta=50, raw=50)
        # open my file
        self.product = qed.h5.reader(uri=self.uri, fapl=fapl).read()
        # all done
        return


# end of file
