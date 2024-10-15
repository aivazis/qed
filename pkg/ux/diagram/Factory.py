# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# superclass
from .Node import Node

# the things i build
from .Label import Label
from .Slot import Slot


# factories
class Factory(Node):
    """
    The representation of a factory
    """

    # public daa
    @property
    def slots(self):
        """
        Get the set of slots that represent my bindings
        """
        # get my cache
        slots = self._slots
        # if it is valid
        if slots is not None:
            # hand it off
            return slots
        # otherwise, initialize it
        slots = set(self.generateSlots())
        # attach it it
        self._slots = slots
        # and return it
        return slots

    # interface
    def connections(self):
        """
        Iterate over my connections to my {slots}
        """
        # go through my slots
        for slot in self.slots:
            # and pass on whatever it knows about me
            yield from slot.connections(factory=self)
        # all done
        return

    # metamethods
    def __init__(self, factory, **kwds):
        # chain up
        super().__init__(**kwds)

        # save the factory
        self.factory = factory
        # and the arity
        self.inputs = len(factory.pyre_inputTraits)
        self.outputs = len(factory.pyre_outputTraits)

        # initialize my slot cache
        self._slots = None

        # all done
        return

    # implementation details
    def generateLabels(self):
        """
        Generate the set of my labels
        """
        # get my type
        family = self.factory.pyre_family().split(".")[-1]
        # the value of the label
        text = [f"{family}"]
        # build the position of the label relative to me
        delta = (0, -2.5)
        # assemble and publish
        yield Label(text=text, category="factory", delta=delta, position=self.position)

        # chain up
        yield from super().generateLabels()

        # all done
        return

    def generateSlots(self):
        """
        Generate the set of my initial slots
        """
        # grab my factory node
        factory = self.factory

        # put all input traits on a pile
        ins = set(factory.pyre_inputTraits)
        # and all output traits on another
        outs = set(factory.pyre_outputTraits)

        # isolate the ones that are just input
        insOnly = ins - outs
        # the ones that are just output
        outsOnly = outs - ins
        # and the ones that are both
        inouts = ins & outs

        # make slots for my inputs
        yield from self._makeInputSlots(traits=insOnly)
        # my outputs
        yield from self._makeOutputSlots(traits=outsOnly)
        # and the slots that are both
        yield from self._makeInOutSlots(traits=inouts)

        # all done
        return

    def rewire(self, new, old):
        """
        Replace {current} by {new} in my {slots}
        """
        # get my slot cache
        slots = self._slots
        # out with the old
        slots.discard(old)
        # in with the new
        slots.add(new)
        # all done
        return self

    # slot generation workhorses
    def _makeInputSlots(self, traits):
        """
        Build input slots for the given {traits}
        """
        # get my location
        x, y = self.position
        # find out how many traits there are; we use this to position the slots in the diagram
        nTraits = len(traits)
        # go through all {traits}
        for idx, trait in enumerate(traits):
            # make a position for this slot
            position = (x - 5, y + 2 * (2 * idx + 1 - nTraits))
            # build an unbound rep
            slot = Slot(product=None, position=position)
            # connect it to me
            slot.connectReader(factory=self, trait=trait)
            # and publish it
            yield slot
        # all done
        return

    def _makeOutputSlots(self, traits):
        """
        Build output slots for all given {traits}
        """
        # get my location
        x, y = self.position
        # find out how many traits there are; we use this to position the slots in the diagram
        nTraits = len(traits)
        # go through all {traits}
        for idx, trait in enumerate(traits):
            # make a position for this slot
            position = (x + 5, y + 2 * (2 * idx + 1 - nTraits))
            # build an unbound rep
            slot = Slot(product=None, position=position)
            # connect it to me
            slot.connectWriter(factory=self, trait=trait)
            # and publish it
            yield slot
        # all done
        return

    def _makeInOutSlots(self, traits):
        """
        Build slots for the given {traits} that both input and output
        """
        # get my location
        x, y = self.position
        # find out how many traits there are; we use this to position the slots in the diagram
        nTraits = len(traits)
        # go through all {traits}
        for idx, trait in enumerate(traits):
            # make a position for this slot
            position = (x, y + 2 * (idx + 1))
            # build an unbound rep
            slot = Slot(product=None, position=position)
            # connect it to me
            slot.connectReader(factory=self, trait=trait)
            slot.connectWriter(factory=self, trait=trait)
            # and publish it
            yield slot
        # all done
        return


# end of file
