# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# base
from .Node import Node


# a property
class Component(Node):
    """
    A component
    """

    # the set of children tags
    elements = "factorymodule", "factoryname", "doc", "property"

    # metamethods
    def __init__(self, attributes, **kwds):
        # chain up
        super().__init__(attributes=attributes, **kwds)
        # my metadata
        self.name = attributes["name"]
        # my factory
        self.module = None
        self.factory = None
        # my documentation
        self.doc = None
        # and my table of properties
        self.properties = {}
        # all done
        return

    # xml event hooks
    def notify(self, parent, **kwds):
        """
        Attach me to my parent
        """
        # add me to my parent's table of properties
        parent.components[self.name] = self
        # all done
        return


# end of file
