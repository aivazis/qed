# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import pyre
import pyre.xml
import pyre.schemata.exceptions


# the base node
class Node(pyre.xml.node):
    """
    Base class for all nodes
    """

    # exceptions
    CastingError = pyre.schemata.exceptions.CastingError

    # metamethods
    def __init__(self, parent, attributes, locator, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the locator
        self.locator = locator
        # all done
        return

    # implementation details
    @classmethod
    def location(cls, path):
        """
        Convert the string in {path} into a path
        """
        # invoke the {pyre} path factory
        return pyre.primitives.path(path)


# end of file
