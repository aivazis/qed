# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclasses
from .Entity import Entity
from .Labeled import Labeled

# things i build
from .Label import Label


# encoding of a relationship between a slot and a factory
class Connector(Labeled, Entity, set):
    """
    Encapsulate the connection between a {factory} and a {slot}
    """

    # interface
    # trait management
    def add(self, trait):
        """
        Add {trait} to the list of connections between my {factory} and my {slot}
        """
        # easy enough
        return super().add(trait)

    def discard(self, trait):
        """
        Add {trait} to the list of connections between my {factory} and my {slot}
        """
        # easy enough
        return super().discard(trait)

    def remove(self, trait):
        """
        Add {trait} to the list of connections between my {factory} and my {slot}
        """
        # easy enough
        return super().remove(trait)

    # label management
    def moved(self):
        """
        Relocate my labels after one of my endpoints has moved
        """
        # compute a new location for my label
        position = self.placeLabel()
        # get my trait label and ask it to move
        self.traitLabel.move(position=position)
        # all done
        return

    # metamethods
    def __init__(self, factory, slot, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the factory
        self.factory = factory
        # and the slot
        self.slot = slot
        # keep track of my trait label
        self.traitLabel = None
        # all done
        return

    # implementation details
    def clear(self):
        """
        Clear out my contents
        """
        # remove my slot
        self.slot = None
        # my factory
        self.factory = None
        # and my labels
        self.traitLabel = None
        self._labels = set()
        # chain up to clear my traits
        return super().clear()

    def generateLabels(self):
        """
        Compute the location of my trait label
        """
        # compute its location
        position = self.placeLabel()

        # make a label with the names of my traits
        label = Label(
            category=self.typename().lower(),
            delta=(0, 0, 0),
            position=position,
            traits=[trait.name for trait in self],
        )
        # save it as my trait label
        self.traitLabel = label
        # publish it
        yield label
        # and chain up
        return super().generateLabels()

    def merge(self, other):
        """
        Assume ownership of the connections managed by {other}
        """
        # transfer the traits in {other} to me
        self |= other
        # rebuild the trait names of my label
        self.traitLabel.traits = [trait.name for trait in self]

        # remove its trait label from its pile
        other._labels.discard(other.traitLabel)
        # transfer the rest of them to my pile
        self._labels |= other._labels

        # all done
        return

    def rewire(self, new):
        """
        Replace the {old} slot with a {new} one
        """
        # easy enough
        self.slot = new
        # all done
        return self

    def placeLabel(self):
        """
        Compute the location of my labels
        """
        # let subclasses handle this
        raise NotImplementedError(f"class '{type(self).__name__}' must override 'placeLabel")


# end of file
