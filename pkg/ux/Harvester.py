# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# configuration harvester
class Harvester:
    """
    Traverse the configuration tree of a configurable and build (name, value) pairs
    for all of its traits
    """

    # interface
    def harvest(self, component):
        """
        Generate a sequence of (fully qualified trait name, trait value) pairs for all properties in
        the configuration tree anchored at {component}
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

    def configure(self, component, reference):
        """
        Mirror the {reference} configuration in {component}
        """
        # go through the {component} properties
        for property in component.pyre_properties():
            # get the name of the property
            name = property.name
            # get the reference value
            value = getattr(reference, name)
            # mirror it
            setattr(component, name, value)

        # now, go through the parts
        for facility in component.pyre_facilities():
            # get the name of the facility
            name = facility.name
            # get the implementations
            src = getattr(reference, name)
            tgt = getattr(component, name)
            # and mirror the configuration
            self.configure(component=tgt, reference=src)

        # all done
        return component


# end of file
