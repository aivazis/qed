# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the base token
class Token:
    """
    Support for turning traits into tokens
    """

    # by default, tokens are visible
    internal = False

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # the default is to do nothing special
        return getattr(descriptor, self.name)

    def str(self, value):
        """
        Build a string representation in normal form
        """
        # by default, leave {value} alone
        return value


# end of file
