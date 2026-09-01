# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
from .Lifecycle import Lifecycle


# a catalog of known data sources
class Sources:
    """
    A catalog of known data sources, their datasets, and where each one stands on its way
    to being viewable
    """

    # interface
    # sources
    def source(self, name):
        """
        Retrieve a data source given its {name}
        """
        # look up the data source safely
        return self._sources.get(name)

    def lifecycle(self, name):
        """
        Retrieve the staging record of the source called {name}, making one on first ask
        """
        # look it up, recording a fresh {connected} standing for sources that have never
        # been asked about
        return self._lifecycles.setdefault(name, Lifecycle())

    def sources(self):
        """
        Retrieve my sources
        """
        # easy enough
        return self._sources.values()

    def addSource(self, source):
        """
        Add a data {source}, or replace the one already registered under its name
        """
        # get the name of the source
        name = source.pyre_name
        # check whether there is an existing source with the same name
        current = self.source(name=name)
        # if there is one
        if current:
            # retire its datasets, since the replacement may have discovered a different
            # set. its place in the pile is deliberately left alone: my order is the order
            # the user registered their products in, and assigning over an existing key
            # keeps it. a source is re-registered when its survey completes, and surveys
            # complete in whatever order the crews get to them, so removing and re-adding
            # would quietly sort the catalog by whichever product finished first
            self._retireDatasets(source=current)
        # add the new source to the pile
        return self._addSource(source=source)

    def removeSource(self, name):
        """
        Remove a source given its {name}
        """
        # look it up
        source = self.source(name=name)
        # if present
        if source:
            # remove it
            self._removeSource(source=source)
        # a departed source takes its staging record with it, so a later reconnection
        # starts out {connected} rather than inheriting a stale standing
        self._lifecycles.pop(name, None)
        # all done
        return source

    # datasets
    def dataset(self, name):
        """
        Retrieve a dataset given its {name}
        """
        # look up the data source safely
        return self._datasets.get(name)

    def datasets(self):
        """
        Retrieve my datasets
        """
        # easy enough
        return self._datasets.values()

    def addDataset(self, dataset):
        """
        Add a dataset
        """
        # get its name
        name = dataset.pyre_name
        # add it to the pile
        self._datasets[name] = dataset
        # all done
        return dataset

    def removeDataset(self, name):
        """
        Remove a dataset given its {name}
        """
        # look it up
        dataset = self._datasets.get(name)
        # if present
        if dataset:
            # remove it
            self._removeDataset(dataset=dataset)
        # all done
        return dataset

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # map: name -> data source
        self._sources = {}
        # map : name -> dataset
        self._datasets = {}
        # map: name -> the staging record of the source; keyed by name rather than held by
        # the source itself, so a record survives the re-registration that follows a survey
        self._lifecycles = {}
        # all done
        return

    def __len__(self):
        """
        Compute the number of registered sources
        """
        # easy enough
        return len(self._sources)

    # implementation details
    # sources
    def _addSource(self, source):
        """
        Add {source}
        """
        # get its name
        name = source.pyre_name
        # add it to the pile
        self._sources[name] = source
        # go through its datasets
        for dataset in source.datasets:
            # and add them to the pile
            self.addDataset(dataset=dataset)
        # all done
        return source

    def _retireDatasets(self, source):
        """
        Drop the datasets of {source} from the index, leaving the source itself alone
        """
        # go through the source datasets
        for dataset in source.datasets:
            # and remove them
            self._removeDataset(dataset=dataset)
        # all done
        return source

    def _removeSource(self, source):
        """
        Remove a source and its datasets
        """
        # its datasets go
        self._retireDatasets(source=source)
        # get the name of the source
        name = source.pyre_name
        # remove it from the pile
        del self._sources[name]
        # the staging record stays: this is also the path a survivor takes when it is
        # re-registered after a survey, and its standing must survive that
        # all done
        return source

    # datasets
    def _removeDataset(self, dataset):
        """
        Remove a dataset
        """
        # get its name
        name = dataset.pyre_name
        # and remove it; tolerate entries that were never indexed, e.g. datasets discovered
        # after their source was registered but before it was re-registered
        self._datasets.pop(name, None)
        # all done
        return dataset


# end of file
