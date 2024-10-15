# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# superclasses
from .Entity import Entity
from .Labeled import Labeled


# the base entity
class Node(Labeled, Entity):
    """
    The base class for diagram nodes
    """

    # interface
    def connections(self):
        """
        Iterate over the nodes that are connected to me
        """
        # i don't have any
        return []

    def move(self, position):
        """
        Move to a new {position}
        """
        # record the new location
        self.position = tuple(position)
        # go through my labels
        for label in self.labels:
            # and ask them to move as well
            label.move(position)
        # notify my connectors
        for connector in self.connections():
            # that they have to update their locations
            connector.moved()

        # all done
        return self

    # metamethods
    def __init__(self, position, **kwds):
        # chain up
        super().__init__(**kwds)
        # save my position
        self.position = tuple(position)
        # all done
        return


# end of file
