# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import inspect
import pyre

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

    # constants
    # how far each end of a factory is from it, along its axis: the end where its inputs meet on
    # one side, and the one where its outputs meet on the other, either of which is a terminal
    # when it has no slots on that side
    reach = 2

    # public data
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

    def given(self):
        """
        The name of the instance i am pinned to: the one a person gave it, possibly empty, or else
        its own; nothing when i am not pinned to an instance
        """
        # get my pin
        pin = self.node.pin
        # if it is not an instance
        if pin is None or isinstance(pin, type):
            # there is no name to give
            return None
        # otherwise, the one a person gave it, or else its own
        return pin.pyre_name if self.alias is None else self.alias

    def family(self):
        """
        The family of the component i am pinned to, if any
        """
        # get my pin
        pin = self.node.pin
        # if there is none
        if pin is None:
            # there is no family
            return None
        # a class has its family, an instance has the one of its class
        return (pin if isinstance(pin, type) else type(pin)).pyre_family()

    def role(self):
        """
        The role of the protocol i satisfy, if it is known
        """
        # get my protocol
        protocol = self.node.protocol
        # and ask it, if there is one
        return None if protocol is None else protocol.pyre_role()

    # metamethods
    def __init__(self, node, **kwds):
        # chain up
        super().__init__(**kwds)

        # save the recipe node i stand for
        self.node = node
        # the name a person gave the instance i am pinned to, which may be empty; none when i am
        # not pinned to an instance, or when nobody named it, in which case its own name is used
        self.alias = None
        # and the arity
        self.inputs = len(node.inputs)
        self.outputs = len(node.outputs)

        # initialize my slot cache
        self._slots = None

        # all done
        return

    # implementation details
    def generateLabels(self):
        """
        Generate the set of my labels
        """
        # build the position of the label relative to me
        delta = (0, -2.5, 0)
        # assemble the parts of what i am, as far as i am pinned, and publish
        yield Label(
            category="factory",
            delta=delta,
            position=self.position,
            given=self.given(),
            family=self.family(),
            role=self.role(),
        )

        # chain up
        yield from super().generateLabels()

        # all done
        return

    def ends(self, position=None):
        """
        The spots of my two ends, where my connectors meet, when i am at {position}, or where i
        am, when it is not given
        """
        # where i am, or would be
        x, y, z = self.position if position is None else position
        # my ends are on either side of me, along my axis
        return [(x - self.reach, y, z), (x + self.reach, y, z)]

    def editable(self, trait):
        """
        Decide whether my {trait} can be changed from the diagram: only the settings of a factory
        pinned to a class or an instance, and only the ones whose value is a single piece of
        text, which components are too, since the framework makes them from their names; maps
        wait for an editor of their own
        """
        # a factory pinned only to its protocol has no settings to change
        if self.node.level == "protocol":
            # so none are
            return False
        # neither are its slots
        if trait.input or trait.output:
            # which hold products
            return False
        # the rest are, unless they are maps
        return not isinstance(trait, pyre.traits.Dict.Dict)

    def methods(self):
        """
        Generate my behaviors that can be invoked with no arguments, the only way the diagram can
        invoke them for now: the ones of my pin, or else the obligations of my protocol
        """
        # get my recipe node
        node = self.node
        # the behaviors are declared by its pin, or else by its protocol
        source = node.protocol if node.pin is None else node.pin
        # the kinds of parameters that a call has to supply when they have no default
        required = (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
        # go through them
        for behavior in source.pyre_behaviors():
            # the parameters of the method, past the instance it is invoked on
            parameters = list(inspect.signature(behavior.pyre_method).parameters.values())[1:]
            # a method that needs an argument waits for a way to supply one
            if any(p.kind in required and p.default is p.empty for p in parameters):
                # so skip it
                continue
            # the rest can be invoked as they are
            yield behavior
        # all done
        return

    def home(self, trait):
        """
        The spot where the slot for {trait} goes when nothing else decides, the way i place my
        slots when i am first drawn
        """
        # get my location
        x, y, z = self.position
        # sort my traits the way i place them
        insOnly, outsOnly, inouts = self.partition()
        # go through the inputs
        for idx, candidate in enumerate(insOnly):
            # if this is the one
            if candidate is trait:
                # it goes on my left
                return (x - 5, y + 2 * (2 * idx + 1 - len(insOnly)), z)
        # go through the outputs
        for idx, candidate in enumerate(outsOnly):
            # if this is the one
            if candidate is trait:
                # it goes on my right
                return (x + 5, y + 2 * (2 * idx + 1 - len(outsOnly)), z)
        # go through the ones that are both
        for idx, candidate in enumerate(inouts):
            # if this is the one
            if candidate is trait:
                # it goes below me
                return (x, y + 2 * (idx + 1), z)
        # a trait that is not mine has no home here
        return None

    def partition(self):
        """
        Sort my traits into the ones that are just input, just output, and both, in the order the
        factory declares them, so the slots line up the same way every time
        """
        # grab my recipe node
        node = self.node
        # all the input traits
        ins = node.inputs
        # and all the output traits
        outs = node.outputs
        # traits overload the comparison operators to build expressions, so membership is
        # decided by identity
        inIds = {id(trait) for trait in ins}
        outIds = {id(trait) for trait in outs}
        # isolate the ones that are just input
        insOnly = [trait for trait in ins if id(trait) not in outIds]
        # the ones that are just output
        outsOnly = [trait for trait in outs if id(trait) not in inIds]
        # and the ones that are both
        inouts = [trait for trait in ins if id(trait) in outIds]
        # hand them off
        return insOnly, outsOnly, inouts

    def generateSlots(self):
        """
        Generate the set of my initial slots
        """
        # sort my traits the way i place them
        insOnly, outsOnly, inouts = self.partition()

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
        x, y, z = self.position
        # find out how many traits there are; we use this to position the slots in the diagram
        nTraits = len(traits)
        # go through all {traits}
        for idx, trait in enumerate(traits):
            # make a position for this slot
            position = (x - 5, y + 2 * (2 * idx + 1 - nTraits), z)
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
        x, y, z = self.position
        # find out how many traits there are; we use this to position the slots in the diagram
        nTraits = len(traits)
        # go through all {traits}
        for idx, trait in enumerate(traits):
            # make a position for this slot
            position = (x + 5, y + 2 * (2 * idx + 1 - nTraits), z)
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
        x, y, z = self.position
        # find out how many traits there are; we use this to position the slots in the diagram
        nTraits = len(traits)
        # go through all {traits}
        for idx, trait in enumerate(traits):
            # make a position for this slot
            position = (x, y + 2 * (idx + 1), z)
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
