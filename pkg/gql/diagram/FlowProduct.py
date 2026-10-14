# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import inspect

# field types
from .FlowFact import FlowFact


# what a slot holds, as the inspector shows it
class FlowProduct(graphene.ObjectType):
    """
    What a slot of a diagram holds: the specification it must satisfy, how far down it is pinned,
    the instance behind it, if any, whether that is stale, and what it says about what it holds
    """

    # the fields
    # the family of the specification it must satisfy
    specification = graphene.String()
    # its documentation
    doc = graphene.String()
    # how far down it is pinned: "protocol", "class", or "instance"; none for a slot that stands
    # for no product and has no instance behind it that holds one
    level = graphene.String()
    # the family of the class of the product, once there is one
    family = graphene.String()
    # the name of the instance: none when there is no instance, empty when nobody named it
    given = graphene.String()
    # whether an instance stands behind the slot, and holds nothing in it
    empty = graphene.Boolean(required=True)
    # whether the product is stale; none when there is no instance
    stale = graphene.Boolean()
    # what it says about what it holds
    facts = graphene.List(graphene.NonNull(FlowFact), required=True)

    # resolvers
    @staticmethod
    def resolve_specification(slot, info, **kwds):
        """
        Get the family of the specification the slot must satisfy
        """
        # get the specification
        spec = slot.specification()
        # and name it by its family
        return None if spec is None else spec.pyre_family()

    @staticmethod
    def resolve_doc(slot, info, **kwds):
        """
        Get the documentation of the specification the slot must satisfy
        """
        # get the specification
        spec = slot.specification()
        # it is its docstring, with the indentation of the source removed
        return None if spec is None else inspect.cleandoc(spec.__doc__ or "")

    @staticmethod
    def resolve_level(slot, info, **kwds):
        """
        Get how far down the product of the slot is pinned
        """
        # the slot knows
        return slot.level()

    @staticmethod
    def resolve_family(slot, info, **kwds):
        """
        Get the family of the class of the product, once there is one
        """
        # find what the slot holds
        _, held = slot.holds()
        # an instance knows its class
        if held is not None:
            # so ask it
            return held.pyre_family()
        # a product pinned to a class
        if slot.product is not None and slot.product.level == "class":
            # is of that one
            return slot.product.pin.pyre_family()
        # otherwise, there is no class yet
        return None

    @staticmethod
    def resolve_given(slot, info, **kwds):
        """
        Get the name of the instance behind the slot, if there is one
        """
        # find what the slot holds
        _, held = slot.holds()
        # nothing has no name, and an instance has its own, or an empty one
        return None if held is None else held.pyre_name or ""

    @staticmethod
    def resolve_empty(slot, info, **kwds):
        """
        Decide whether there is an instance behind the slot that holds nothing in it
        """
        # find what the slot holds
        behind, held = slot.holds()
        # and decide
        return behind and held is None

    @staticmethod
    def resolve_stale(slot, info, **kwds):
        """
        Decide whether the product the slot holds is stale, if it holds one
        """
        # find what the slot holds
        _, held = slot.holds()
        # nothing has no status; the rest know theirs
        return None if held is None else bool(held.pyre_stale)

    @staticmethod
    def resolve_facts(slot, info, **kwds):
        """
        Collect what the product says about what it holds
        """
        # find what the slot holds
        _, held = slot.holds()
        # the products that can describe themselves
        describe = getattr(held, "pyre_describe", None)
        # nothing, or a product that cannot
        if describe is None:
            # says nothing
            return []
        # the rest say what they hold
        return [FlowFact(name=name, value=value) for name, value in describe()]


# end of file
