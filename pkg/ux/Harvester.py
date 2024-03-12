# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# configuration harvester
class Harvester:
    """
    Traverse the configuration tree of a configurable and build (name, value) pairs
    for all of its traits
    """

    # interface
    def harvest(self, component):
        """
        Generate a sequence of (fully qualified trait name, trait value) for all properties
        in the configuration tree anchored at {component}
        """
        # get the component name
        context = component.pyre_name
        # go through the {component} properties
        for property in component.pyre_properties():
            # get the property name
            name = property.name
            # form the fully qualified name
            address = f"{context}.{name}"
            # get the value
            value = getattr(component, name)
            # and return the pair
            yield address, value

        # no go through the parts
        for facility in component.pyre_facilities():
            # get the value
            implementation = getattr(component, facility.name)
            # and get it to render its configuration
            yield from self.harvest(component=implementation)

        # all done
        return

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # initialize the component context; used to record owner information for
        # component hierarchies
        self.context = None
        # all done
        return


# end of file
