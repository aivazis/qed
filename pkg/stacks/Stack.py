# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# a stack of readers, presented to the rest of {qed} as an aggregate reader
class Stack(
    qed.flow.factory, family="qed.readers.stack", implements=qed.protocols.reader
):
    """
    A stack of readers whose datasets are rendered through aggregate channels
    """

    # user configurable state
    # the uri of my data source; synthetic, since a stack spans many files
    uri = qed.properties.uri()
    uri.doc = "the uri of the data source"

    # the map of selector names to their allowed values
    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"

    # a key value store of preferred values for selectors
    selections = qed.properties.kv()
    selections.doc = "a key value store of preferred values for selectors"

    # the aggregate datasets i expose, one per selector assignment my members share
    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the aggregate datasets i expose"

    # my member readers
    readers = qed.properties.list(schema=qed.protocols.reader())
    readers.doc = "the readers of my stack"

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
        # go through the matches
        for dataset in self.select(selector=selector):
            # and hand off the first one
            return dataset
        # otherwise, there is no match
        return None

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # get my members
        readers = self.readers
        # if i somehow have none
        if not readers:
            # there is nothing to aggregate
            return
        # the first member is my reference for the shared selector spec
        head, *_ = readers
        # adopt its selector spec
        self.selectors = head.selectors
        # its availability map
        self.available = head.available
        # and its preferred selections
        self.selections = head.selections
        # synthesize a uri that identifies me
        self.uri = f"stack:{self.pyre_name}"
        # build my aggregate datasets
        self._loadDatasets()
        # all done
        return

    # implementation details
    def _loadDatasets(self):
        """
        Build one aggregate dataset per selector assignment shared by all my members
        """
        # get my members
        readers = self.readers
        # the first member enumerates the candidate selector assignments
        head, *_ = readers
        # go through its datasets
        for reference in head.datasets:
            # the selector that identifies this dataset
            selector = reference.selector
            # gather the matching dataset from each member
            members = [reader.find(selector) for reader in readers]
            # if any member is missing this assignment
            if any(member is None for member in members):
                # skip it; the stack is only as wide as its narrowest member
                continue
            # name the aggregate after me and the selector values
            suffix = ".".join(str(value) for value in selector.values())
            # form the full name
            name = f"{self.pyre_name}.{suffix}"
            # build the aggregate dataset over the gathered members
            dataset = qed.stacks.dataset(
                name=name, members=members, selector=dict(selector)
            )
            # and add it to my pile
            self.datasets.append(dataset)
        # all done
        return


# end of file
