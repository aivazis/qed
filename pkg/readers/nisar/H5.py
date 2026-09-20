# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections

# support
import qed

# the lookup of access credentials
from .. import access


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
    datasets.persistent = False

    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"
    selectors.persistent = False

    selections = qed.properties.kv()
    selections.doc = "a key value store of preferred values for selectors"

    pages = qed.properties.int()
    pages.default = 1024**2
    pages.doc = "the number of 4K pages in the aggregation cache"

    credentials = qed.properties.kv()
    credentials.doc = "how to get access to my product, e.g. the AWS {profile} and {region}"

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
    def grant(self, resolve=True):
        """
        Assemble what gets presented to the infrastructure in order to open my product

        The grant starts out empty. If an archive manages me, what it hands out goes in first,
        fresh every time, since whoever is asking may be about to ship it to a worker that
        cannot reach the archive, and a grant that was taken once and kept would outlive the
        token it carries. My own {credentials} go in last and win, so that i can be wired by
        hand, and so that i can outlive the archive i came from. With {resolve}, whatever is
        still missing is looked up, e.g. keys for a bucket through the standard AWS chain,
        under the profile the grant names; describing work for somebody else to do leaves that
        lookup to them, since they are the ones who are going to open the product

        My {credentials} are what the user wrote, and they are all that is ever saved. The
        grant lives in memory only
        """
        # start with nothing
        grant = {}
        # get my archive
        archive = self._archive
        # if i am managed
        if archive is not None:
            # start with what it hands out
            grant.update(archive.credentials())
        # my own settings win
        grant.update(dict(self.credentials))
        # if my caller is the one who opens the product
        if resolve:
            # fill in what is still missing
            grant = access.resolve(uri=self.uri, grant=grant)
        # hand it off
        return grant

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
        # assemble what it takes to get at my product, looking up whatever is missing
        credentials = self.grant()
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

        # first contact is complete, and only now is it safe to say so: everything that
        # could fail is behind me, so a failed attempt leaves no trace and can be repeated
        self._opened = True
        # all done
        return self

    # metamethods
    def __init__(self, archive=None, fapl=None, **kwds):
        # chain up; construction is passive, so nothing touches the file until {open}
        super().__init__(**kwds)
        # first contact has not been made; this is the state of an instance, so it is set
        # here rather than shared through the class
        self._opened = False
        # squirrel away what first contact needs
        self._archive = archive
        self._fapl = fapl
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
    _archive = None  # the archive that manages my data source, when there is one
    _fapl = None  # the file access property list i was constructed with


# end of file
