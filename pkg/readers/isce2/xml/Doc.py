# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# base
from .Node import Node


# capture the property documentation
class Doc(Node):
    """
    Property documentation
    """

    # doc nodes don't have children
    elements = ()

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the harvested value
        self.doc = None
        # all done
        return

    # xml event hooks
    def notify(self, parent, **kwds):
        """
        Decorate my parent with my value
        """
        # set my parent's doc
        parent.doc = self.doc
        # all done
        return

    def content(self, text, **kwds):
        """
        Capture my body text
        """
        # store the text as my value
        self.doc = text
        # all done
        return


# end of file
