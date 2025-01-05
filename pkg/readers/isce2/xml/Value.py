# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# base
from .Node import Node


# capture the value of a property
class Value(Node):
    """
    A property value
    """

    # value nodes don't have children
    elements = ()

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the harvested value
        self.value = None
        # all done
        return

    # xml event hooks
    def notify(self, parent, **kwds):
        """
        Decorate my parent with my value
        """
        # set my parent's value
        parent.value = self.value
        # all done
        return

    def content(self, text, **kwds):
        """
        Capture my body text
        """
        # store the text as my value; don't attempt to cast to anything in the absence of an actual
        # schema for the configuration files
        self.value = text
        # all done
        return


# end of file
