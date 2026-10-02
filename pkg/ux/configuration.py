# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections
import collections.abc

# support
import pyre


def configuration(*, roots) -> list:
    """
    Describe the configuration of every component reachable from the components in {roots}
    through their traits: the value of each trait, where the value came from, and the components
    it refers to

    Components may refer to each other, so each one is described once, in the order the walk
    reaches it, and a reference to it is reported by name. The values of secret traits are not
    described
    """
    # the components waiting to be described, each root once
    pending = collections.deque()
    # the ones reached so far
    reached = set()
    # go through the roots
    for root in roots:
        # a root reached already
        if id(root) in reached:
            # is not described twice
            continue
        # the rest are waiting
        reached.add(id(root))
        pending.append(root)
    # the descriptions
    components = []
    # go through the components
    while pending:
        # the next one
        component = pending.popleft()
        # its inventory knows where each value came from
        inventory = component.pyre_inventory
        # the descriptions of its traits
        traits = []
        # go through its configurable traits
        for trait in component.pyre_configurables():
            # the value
            value = getattr(component, trait.name)
            # the components it refers to
            references = list(_components(value=value))
            # go through them
            for reference in references:
                # a component reached for the first time
                if id(reference) not in reached:
                    # is described later
                    reached.add(id(reference))
                    pending.append(reference)
            # where the value came from
            priority = inventory.getTraitPriority(trait)
            locator = inventory.getTraitLocator(trait)
            # describe the trait
            traits.append(
                {
                    "name": trait.name,
                    "kind": "facility" if trait.isFacility else "property",
                    "schema": trait.typename,
                    "value": None if trait.secret else _render(value=value),
                    "secret": trait.secret,
                    "priority": priority.name if priority is not None else None,
                    "locator": str(locator) if locator is not None else None,
                    "components": [reference.pyre_name for reference in references],
                }
            )
        # describe the component
        components.append(
            {
                "name": component.pyre_name,
                "family": component.pyre_family(),
                "traits": traits,
            }
        )
    # all done
    return components


# implementation details
def _components(*, value):
    """
    Generate the components in {value}: the value itself, or the members of a collection
    """
    # a component
    if isinstance(value, pyre.component):
        # is itself
        yield value
        # and that is all
        return
    # a mapping, including the ones pyre builds for the values of its dictionary traits
    if isinstance(value, collections.abc.Mapping):
        # holds its components among its values
        value = value.values()
    # a collection other than a string of characters or of bytes
    if isinstance(value, collections.abc.Collection) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        # holds its components among its members
        yield from (member for member in value if isinstance(member, pyre.component))
    # all done
    return


def _render(*, value):
    """
    Render {value} as a string, naming the components in it
    """
    # nothing
    if value is None:
        # is nothing
        return None
    # a component
    if isinstance(value, pyre.component):
        # is its name
        return value.pyre_name
    # a mapping, including the ones pyre builds for the values of its dictionary traits
    if isinstance(value, collections.abc.Mapping):
        # is its entries
        return str({key: _name(value=member) for key, member in value.items()})
    # a collection
    if isinstance(value, (list, tuple, set, frozenset)):
        # is its members
        return str([_name(value=member) for member in value])
    # anything else
    return str(value)


def _name(*, value):
    """
    Name {value}, if it is a component, or hand it back as is
    """
    # a component is named by its name, and anything else is itself
    return value.pyre_name if isinstance(value, pyre.component) else value


# end of file
