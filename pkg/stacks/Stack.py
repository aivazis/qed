# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections

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

    def member(self, index, selector):
        """
        Retrieve the dataset of my {index}-th member that matches {selector}
        """
        # get the member reader
        reader = self.readers[index]
        # and ask it for the dataset that matches {selector}
        return reader.find(selector=selector)

    def memberAvailable(self, index):
        """
        Retrieve the availability map of my {index}-th member
        """
        # a pinned member can realize more combos than the aggregate; hand off its own map
        return self.readers[index].available

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # get my members
        readers = self.readers
        # remember how many members i have
        self.extent = len(readers)
        # if i somehow have none
        if not readers:
            # there is nothing to aggregate
            return
        # the selector SPEC is shared by every member by construction, so i can borrow it
        head, *_ = readers
        # from the first member
        self.selectors = head.selectors
        # synthesize a uri that identifies me
        self.uri = f"stack:{self.pyre_name}"
        # build my aggregate datasets, one per combo that every member realizes
        self._loadDatasets()
        # my availability is what those aggregate datasets actually realize: the intersection
        # across all members, NOT any one member's; derive it from the datasets themselves, the
        # way a reader derives its own availability (this also auto-selects single-valued axes)
        self.available = self._checkAvailability()
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

    def _checkAvailability(self):
        """
        Build a map with the available values of each selector, from my aggregate datasets
        """
        # get my selector spec
        selectors = self.selectors
        # the values that appear in at least one of my aggregate datasets
        available = collections.defaultdict(set)
        # go through my aggregate datasets
        for dataset in self.datasets:
            # for each selector axis
            for axis in selectors:
                # record the value this dataset realizes
                available[axis].add(dataset.selector[axis])
        # get my selections
        selections = self.selections
        # go through the available options
        for axis, options in available.items():
            # if an axis has exactly one option
            if len(options) == 1:
                # get it
                option, *_ = options
                # and select it on the user's behalf
                selections[axis] = option
        # all done
        return available


# end of file
