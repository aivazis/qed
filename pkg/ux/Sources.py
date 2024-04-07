# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# a catalog of known data sources
class Sources:
    """
    A catalog of known data sources and their datasets
    """

    # interface
    # sources
    def source(self, name):
        """
        Retrieve a data source given its {name}
        """
        # look up the data source safely
        return self._sources.get(name)

    def sources(self):
        """
        Retrieve my sources
        """
        # easy enough
        return self._sources.values()

    def addSource(self, source):
        """
        Add a data {source}
        """
        # get the name of the source
        name = source.pyre_name
        # check whether there is an existing source with the same name
        current = self.source(name=name)
        # if there is one
        if current:
            # remove it
            self._removeSource(source=current)
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

    def _removeSource(self, source):
        """
        Remove a source and its datasets
        """
        # go through the source datasets
        for dataset in source.datasets:
            # and remove them
            self._removeDataset(dataset=dataset)
        # get the name of the source
        name = source.pyre_name
        # remove it from the pile
        del self._sources[name]
        # all done
        return source

    # datasets
    def _removeDataset(self, dataset):
        """
        Remove a dataset
        """
        # get its name
        name = dataset.pyre_name
        # and remove it
        del self._datasets[name]
        # all done
        return dataset


# end of file
