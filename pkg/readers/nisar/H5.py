# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import collections

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

        # load the datasets
        self._loadDatasets()
        # and build the build the selector availability map
        self.available = self._checkAvailability()

        # all done
        return

    # implementation details
    def _checkAvailability(self):
        """
        Build a map with the available values of each selector
        """
        # initialize the map
        available = collections.defaultdict(set)
        # go through my datasets
        for dataset in self.datasets:
            # and their selectors
            for axis, coordinate in dataset.selector.items():
                # and add the {coordinate} as a possible value of {axis}
                available[axis].add(coordinate)
        # all done
        return available


# end of file
