# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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
        Indicate whether this slot stands for a product of the recipe
        """
        # easy enough
        return self.product is not None

    # interface
    def specification(self):
        """
        What i must hold: the specification of my product, or else the one the trait i belong to
        expects
        """
        # get my product
        product = self.product
        # if i stand for one that has a specification
        if product is not None and product.specification is not None:
            # that is it
            return product.specification
        # otherwise, go through my connections
        for connector in self.connections():
            # and the traits of each one
            for trait in connector:
                # the first one says
                return trait.protocol
        # i have no connections, which a slot on a diagram always has
        return None

    def level(self):
        """
        How far down what i hold is pinned: my product's level, when i stand for one, or else
        "instance" when an instance holds a product in me; nothing otherwise
        """
        # get my product
        product = self.product
        # if i stand for one
        if product is not None:
            # ask it
            return product.level
        # otherwise, find what i hold
        behind, held = self.holds()
        # a product held by an instance is an instance; anything else has no level
        return "instance" if behind and held is not None else None

    def holds(self):
        """
        What i hold, as a pair: whether there is an instance behind me, and the product it holds,
        possibly none; a product of the recipe holds its instance once it is one, and a trait's
        own slot holds whatever the instance of its factory holds in it
        """
        # get my product
        product = self.product
        # if i stand for one
        if product is not None:
            # it holds its instance, once it is one
            return (True, product.pin) if product.level == "instance" else (False, None)
        # otherwise, go through my connections
        for connector in self.connections():
            # to the factory behind each one
            node = connector.factory.node
            # a factory that is not an instance
            if node.level != "instance":
                # holds nothing yet
                continue
            # otherwise, the trait it connects me to
            for trait in connector:
                # holds whatever the instance has in it
                return True, node.pin.pyre_inventory[trait].value
        # no instance is behind me
        return False, None

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

        # make my labels, if i haven't yet, so they reflect me before i take anything over
        self.labels
        # take over the product of {other}, if it has one
        self.rebind(other=other)
        # take ownership of all the labels attached to {other}
        self.relabel(other=other, delta=deltaLabels)
        # connectors
        self.rewire(other=other, deltaLabels=deltaLabels, deltaConnectors=deltaConnectors)

        # return the changes
        return other, deltaLabels, deltaConnectors

    # metamethods
    def __init__(self, product=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the product of the recipe i stand for, if any
        self.product = product

        # a map from readers to the associated connectors
        self.readers = {}
        # and another for writers
        self.writers = {}

        # all done
        return

    def __str__(self):
        # build the binding decoration
        bound = "(bound)" if self.bound else "(unbound)"
        # add it to my textual representation
        return " ".join([super().__str__(), bound])

    # implementation details
    def generateLabels(self):
        """
        Generate the set of my labels
        """
        # grab my product
        product = self.product
        # i only get a label if i'm bound to a product the user specialized by pinning it; until
        # then i only join the slots of factories, and their connectors say all there is to say
        if product is not None and product.pin is not None:
            # build the position of the label relative to me
            delta = (0, -1, 0)
            # assemble the parts of what my product is, and publish
            yield Label(
                category="product",
                delta=delta,
                position=self.position,
                given=self.given(),
                family=self.family(),
            )

        # chain up
        yield from super().generateLabels()

        # all done
        return

    def given(self):
        """
        The name of the instance my product is pinned to, which is also how separately drawn
        graphs join; nothing when it is not pinned to an instance
        """
        # get the pin of my product
        pin = self.product.pin
        # if it is not an instance
        if pin is None or isinstance(pin, type):
            # there is no name to give
            return None
        # otherwise, its own, which is empty when it has none
        return pin.pyre_name or ""

    def family(self):
        """
        The family of the component my product is pinned to
        """
        # get the pin of my product
        pin = self.product.pin
        # a class has its family, an instance has the one of its class
        return (pin if isinstance(pin, type) else type(pin)).pyre_family()

    def rebind(self, other):
        """
        Take over the product of {other}, if i do not have one of my own; the recipe is the
        diagram's to update
        """
        # if i have no product and {other} does
        if self.product is None and other.product is not None:
            # it is mine now
            self.product = other.product
        # all done
        return

    def relabel(self, other, delta):
        """
        Merge the labels of {other} into my pile
        """
        # for now, just merge the labels of {other} into my pile
        self._labels |= other.labels
        # and claim them
        for label in other.labels:
            # so they follow me from now on
            label.owner = self

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
