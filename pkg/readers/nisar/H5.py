# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections

# support
import qed


# the basic reader for products in HDF5 format
class H5(qed.flow.factory, family="qed.readers.nisar.h5", implements=qed.protocols.reader):
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
    pages.default = 1024**2
    pages.doc = "the number of 4K pages in the aggregation cache"

    # constants
    # my datasets can describe themselves in a discovery record and materialize as
    # metadata-only twins, so my first contact can happen on a crew member
    surveyable = True

    # public data
    @property
    def granule(self):
        """
        The identifier the product carries for itself
        """
        # a reader that was told, e.g. one hydrated from a survey, answers with what it
        # was told
        if self._granule is not None:
            # since it never opens the file
            return self._granule
        # a product that has not been opened cannot say
        if self.product is None:
            # so it does not
            return None
        # carefully, since a malformed product may be missing the group that says so
        try:
            # every NISAR product identifies itself here, and the granule id is unique,
            # versioned, and meaningful to the people who produced it -- which makes it
            # the right name for anything derived from this product
            return str(self.product.science.LSAR.identification.granuleId)
        # a product that does not carry one
        except AttributeError:
            # cannot be named this way
            return None

    @granule.setter
    def granule(self, value):
        """
        Adopt {value} as the identifier of my product, on the word of whoever opened it
        """
        # remember it
        self._granule = value
        # all done
        return

    # interface
    def select(self, selector):
        """
        Retrieve all datasets that match {selector}
        """
        # go through my datasets
        for dataset in self.datasets:
            # get their selectors
            spec = dataset.selector
            # go through the constraints provided by the user
            for key, value in selector.items():
                # if it's not a match
                if spec[key] != value:
                    # bail
                    break
            # if everything matched
            else:
                # hand the dataset off
                yield dataset

        # all done
        return

    def find(self, selector):
        """
        Retrieve the first dataset that matches {selector}
        """
        # go through my datasets
        for dataset in self.datasets:
            # get their selectors
            spec = dataset.selector
            # go through the constraints provided by the user
            for key, value in selector.items():
                # if it's not a match
                if spec[key] != value:
                    # bail
                    break
            # if everything matched
            else:
                # hand the dataset off
                return dataset
        # all done
        return

    @qed.export
    def open(self, measure=True):
        """
        Establish first contact with the data source: open the file, walk its structure,
        discover the datasets, and derive the selector availability
        """
        # if i have already made contact
        if self._opened:
            # there is nothing further to do
            return self
        # leave a mark
        self._opened = True
        # get the access property list i was constructed with
        fapl = self._fapl
        # if the caller didn't provide one
        if fapl is None:
            # make a default one
            fapl = qed.h5.libh5.properties.fapl()
        # get the number of pages to set aside for the page aggregator
        pages = self.pages
        # if it is non-trivial
        if pages:
            # form the cache size
            size = 4 * 1024 * pages
            # adjust the {fapl}
            fapl.pageBufferSize = qed.h5.libh5.properties.PageBuffer(bytes=size, metadata=5, raw=50)
        # if i'm managed, get access credentials from the archive; otherwise settle for
        # whatever the caller supplied, e.g. a worker rebuilding me from a recipe
        archive = self._archive
        credentials = archive.credentials() if archive else (self.credentials or {})
        # retain them, so my recipe can carry them to a worker that cannot reach the archive
        self.credentials = credentials
        # open my file
        self.product = qed.h5.reader(uri=self.uri, credentials=credentials, fapl=fapl).read()

        # load the datasets
        self._loadDatasets()
        # and build the selector availability map
        self.available = self._checkAvailability()

        # unless my caller is a worker that will be handed the client's controller state,
        # let each dataset sample itself, so its channels start out tuned to its data
        if measure:
            # go through the datasets i discovered
            for dataset in self.datasets:
                # and let each one measure itself
                dataset.measure()

        # all done
        return self

    # metamethods
    def __init__(self, archive=None, credentials=None, fapl=None, **kwds):
        # chain up; construction is passive, so nothing touches the file until {open}
        super().__init__(**kwds)
        # squirrel away what first contact needs
        self._archive = archive
        self._fapl = fapl
        # retain whatever credentials the caller supplied; {open} may refresh them from
        # the archive
        self.credentials = credentials or {}
        # initialize the availability map so the panel can render before first contact
        self.available = {}
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

    # private data
    product = None  # the opened data product, once first contact has been made
    _granule = None  # the identifier of my product, when i was told rather than read it
    _opened = False  # whether first contact has been made
    _archive = None  # the archive that manages my data source, when there is one
    _fapl = None  # the file access property list i was constructed with


# end of file
