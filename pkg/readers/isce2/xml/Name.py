# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# base
from .Node import Node


# capture the component name
class Name(Node):
    """
    The component name
    """

    # name nodes don't have children
    elements = ()

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the harvested value
        self.name = None
        # all done
        return

    # xml event hooks
    def notify(self, parent, **kwds):
        """
        Decorate my parent with my value
        """
        # set my parent's value
        parent.factory = self.name
        # all done
        return

    def content(self, text, **kwds):
        """
        Capture my body text
        """
        # store the text as the component name
        self.name = text
        # all done
        return


# end of file
