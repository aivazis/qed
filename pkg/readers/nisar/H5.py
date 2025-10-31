# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


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

    selections = qed.properties.kv()
    selections.doc = "a key value store of preferred values for selectors"

    pages = qed.properties.int()
    pages.default = None
    pages.doc = "the number of 4K pages in the aggregation cache"

    # metamethods
    def __init__(self, archive=None, fapl=None, **kwds):
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
            fapl.setPageBufferSize(page=size, meta=5, raw=50)
        # if i'm managed, get access credentials from the archive
        credentials = archive.credentials() if archive else {}
        # open my file
        self.product = qed.h5.reader(
            uri=self.uri, credentials=credentials, fapl=fapl
        ).read()

        # load the datasets
        self._loadDatasets()
        # and build the selector availability map
        self.available = self._checkAvailability()

        # all done
        return

    # implementation details
    def _checkAvailability(self):
        """
        Build a map with the available values of each selector
        """
        # get the map of the required selector values
        selectors = self.selectors
        # initialize the map of available values, i.e. values that are present as selections in at
        # least one known dataset
        available = collections.defaultdict(set)
        # go through my datasets
        for dataset in self.datasets:
            # for each known legal axis
            for axis in selectors:
                # add the corresponding value from this dataset to the {available} pile
                available[axis].add(dataset.selector[axis])
        # now, get my selections
        selections = self.selections
        # and go through the options
        for axis, options in available.items():
            # if there is only one option
            if len(options) == 1:
                # get the setting
                option, *_ = options
                # and select it
                selections[axis] = option
        # all done
        return available


# end of file
