# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# base
from .Node import Node


# a property
class Property(Node):
    """
    A property
    """

    # properties have values and documentation
    elements = "value", "doc"

    # metamethods
    def __init__(self, attributes, **kwds):
        # chain up
        super().__init__(attributes=attributes, **kwds)
        # my name
        self.name = attributes["name"]
        # my value
        self.value = None
        # my documentation
        self.doc = None
        # all done
        return

    # xml event hooks
    def notify(self, parent, **kwds):
        """
        Attach me to my parent
        """
        # add me to my parent's table of properties
        parent.properties[self.name] = self
        # all done
        return


# end of file
