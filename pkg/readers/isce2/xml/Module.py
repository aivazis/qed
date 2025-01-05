# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# base
from .Node import Node


# capture the component declaration module
class Module(Node):
    """
    The declaration module of a component
    """

    # module nodes don't have children
    elements = ()

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the harvested value
        self.module = None
        # all done
        return

    # xml event hooks
    def notify(self, parent, **kwds):
        """
        Decorate my parent with my value
        """
        # set my parent's module name
        parent.module = self.module
        # all done
        return

    def content(self, text, **kwds):
        """
        Capture my body text
        """
        # store the text as my module name
        self.module = text
        # all done
        return


# end of file
