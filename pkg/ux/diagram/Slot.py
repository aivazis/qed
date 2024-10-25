# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# superclass
from .Node import Node

# the things i build
from .Label import Label
from .Input import Input
from .Output import Output


# slots, both bound and unbound
class Slot(Node):
    """
    The representation of a slot
    """

    # properties
    @property
    def bound(self):
        """
        Indicate whether this slot is associated with an actual product
        """
        return self.product is not None

    # interface
    def connectReader(self, factory, trait):
        """
        Make a connection between {factory} and me for the given input {trait}
        """
        # look up {factory} in my index of {readers}
        connector = self.readers.get(factory)
        # if it's not there
        if connector is None:
            # make a new one
            connector = Input(factory=factory, slot=self)
            # add it to the pile
            self.readers[factory] = connector
        # add this {trait} to the connection
        connector.add(trait)
        # all done
        return

    def connectWriter(self, factory, trait):
        """
        Make a connection between {factory} and me for the given output {trait}
        """
        # look up {factory} in my index of {writers}
        connector = self.writers.get(factory)
        # if it's not there
        if connector is None:
            # make a new one
            connector = Output(factory=factory, slot=self)
            # add it to the pile
            self.writers[factory] = connector
        # add this {trait} to the connection
        connector.add(trait)
        # all done
        return

    def connections(self, factory=None):
        """
        Iterate over my connections
        """
        # if the caller doesn't care about a particular factory
        if factory is None:
            # go through my readers
            yield from self.readers.values()
            # and my writers
            yield from self.writers.values()
            # all done
            return

        # otherwise, look up factory in my readers
        connection = self.readers.get(factory)
        # if it's there
        if connection:
            # make it available
            yield connection
        # now, check among the writers
        connection = self.writers.get(factory)
        # if there
        if connection:
            # make it available
            yield connection

        # all done
        return

    def merge(self, other):
        """
        Take over all relationship managed by {other} and clear it out
        """
        # make the label update piles
        newLabels = []
        delLabels = []
        updatedLabels = []
        # pack them in a pile
        deltaLabels = newLabels, delLabels, updatedLabels
        # and the connection update piles
        newConnectors = []
        delConnectors = []
        updatedConnectors = []
        # pack them in a pile
        deltaConnectors = newConnectors, delConnectors, updatedConnectors

        # take care of the flow
        self.rebind(other=other)
        # take ownership of all the labels attached to {other}
        self.relabel(other=other, delta=deltaLabels)
        # connectors
        self.rewire(
            other=other, deltaLabels=deltaLabels, deltaConnectors=deltaConnectors
        )

        # return the changes
        return other, deltaLabels, deltaConnectors

    # metamethods
    def __init__(self, product=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the product
        self.product = product

        # a map from readers to the associated connectors
        self.readers = {}
        # and another for writers
        self.writers = {}

        # all done
        return

    def __str__(self):
        # build the binding decoration
        bound = "(unbound)" if self.bound else "(bound)"
        # add it to my textual representation
        return " ".join([super().__str__(), bound])

    # implementation details
    def generateLabels(self):
        """
        Generate the set of my labels
        """
        # grab my product
        product = self.product
        # i only get a label if i'm bound
        if product is not None:
            # get my name
            name = self.name or ""
            # get my type
            family = product.pyre_family().split(".")[-1]
            # the value of the label
            text = [f"{name}:{family}"]
            # build the position of the label relative to me
            delta = (0, -1)
            # assemble and publish
            yield Label(
                text=text, category="product", delta=delta, position=self.position
            )

        # chain up
        yield from super().generateLabels()

        # all done
        return

    def rebind(self, other):
        """
        Examine {other} and me, and rebind the flow so that {other} can be released
        after {merge}
        """
        # get my product
        product = self.product
        # if i'm the one that's bound
        if product is not None:
            # go through all the connections in {other}
            for connector in other.connections():
                # get the factory
                factory = connector.factory
                # go through all the traits
                for trait in connector:
                    # and bind them to my product
                    setattr(factory, trait.name, product)

        # ask {other} for its binding
        product = other.product
        # if it is bound
        if product is not None:
            # bind me
            self.product = product
            # go through my connections
            for connector in self.connections():
                # get the associated factory
                factory = connector.factory
                # go through all the traits
                for trait in connector:
                    # and bind them to my new product
                    setattr(factory, trait.name, product)

        # all done
        return

    def relabel(self, other, delta):
        """
        Merge the labels of {other} into my pile
        """
        # for now, just merge the labels of {other} into my pile
        self._labels |= other.labels

        # N.B. this doesn't generate any deltas: labels are free-standing and the change of
        # ownership is transparent. this depends on how we manage the {relay} store on
        # the client; an earlier implementation derived label ids from the owner's, making
        # change of ownership visible to the client
        # send back the deltas
        return other, delta

    def rewire(self, other, deltaLabels, deltaConnectors):
        """
        Merge the connectors of {other} into my pile
        """
        # rewire my readers
        self.rewireConnectors(
            other=other,
            myPile=self.readers,
            herPile=other.readers,
            deltaLabels=deltaLabels,
            deltaConnectors=deltaConnectors,
        )
        # and my writers
        self.rewireConnectors(
            other=other,
            myPile=self.writers,
            herPile=other.writers,
            deltaLabels=deltaLabels,
            deltaConnectors=deltaConnectors,
        )

        # all done
        return other, deltaLabels, deltaConnectors

    def rewireConnectors(self, other, myPile, herPile, deltaLabels, deltaConnectors):
        """
        Merge {herPile} of connectors into {myPile}
        """
        # unpack the label deltas
        _, delLabels, updatedLabels = deltaLabels
        # and the connector deltas
        _, delConnectors, _ = deltaConnectors

        # go through the {herPile}
        for factory, connector in herPile.items():
            # look up the {factory} in {myPile}
            mine = myPile.get(factory)
            # if i have one
            if mine is not None:
                # schedule an update for my label
                updatedLabels.append(mine.traitLabel)
                # put the connector on the discard pile
                delConnectors.append(connector)
                # put its trait label on the discard pile
                delLabels.append(connector.traitLabel)
                # merge the two connectors
                mine.merge(other=connector)
                # and clear out the obsolete {connector}
                connector.clear()
            # if i don't have a connection to this factory
            else:
                # move the connector and its label as they are to my pile
                myPile[factory] = connector
                # rewire the factory
                factory.rewire(new=self, old=other)
                # and the connector
                connector.rewire(new=self)

        # all done
        return other, deltaLabels, deltaConnectors


# end of file
