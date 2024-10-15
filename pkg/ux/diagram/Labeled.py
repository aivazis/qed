# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# mixin that provides access to a set of labels
class Labeled:
    """
    Mixin that manages a set of labels associated with an entity
    """

    # public data
    @property
    def labels(self):
        """
        Get the set of my labels
        """
        # get my cache
        labels = self._labels
        # if it is valid
        if labels is not None:
            # hand it off
            return labels
        # otherwise, initialize it
        labels = set(self.generateLabels())
        # attach it it
        self._labels = labels
        # and return it
        return labels

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # initially, my label cache is invalid
        self._labels = None
        # all done
        return

    # implementation details
    # label generation hook
    def generateLabels(self):
        """
        Build my intrinsic labels
        """
        # i have none
        return []


# end of file
