# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the data transfer priority group
class Priority(Numeric):
    """
    The data transfer priority group
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # form the recognizer
        return rf"G(?P<{self.name}>\d\d)"

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # ask my superclass to generate
        gid = super().gid(descriptor=descriptor)
        # add my prefix and render
        return f"G{gid}"

    # metamethods
    def __init__(self, default=0, **kwds):
        # chain up
        super().__init__(default=default, low=0, high=100, width=2, **kwds)
        # set up my docstring
        self.__doc__ = "priority group"
        # all done
        return


# end of file
