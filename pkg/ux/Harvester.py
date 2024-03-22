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
        # initialize the pile
        configuration = {}
        # go through the {component} properties
        for property in component.pyre_properties():
            # get the name of the property
            name = property.name
            # get the value
            value = getattr(component, name)
            # and store it
            configuration[property.name] = value

        # now, go through the parts
        for facility in component.pyre_facilities():
            # get the name of the facility
            name = facility.name
            # get the implementation
            implementation = getattr(component, name)
            # and harvest its configuration
            configuration[name] = self.harvest(component=implementation)

        # all done
        return configuration


# end of file
