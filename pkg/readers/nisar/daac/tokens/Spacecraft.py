# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the spacecraft id
class Spacecraft(Numeric):
    """
    The spacecraft id
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # form the recognizer
        return rf"S(?P<{self.name}>\d\d\d)"

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # ask my superclass to generate
        gid = super().gid(descriptor=descriptor)
        # add my prefix and render
        return f"S{gid}"

    # metamethods
    def __init__(self, default=0, **kwds):
        # chain up
        super().__init__(default=default, low=0, high=1000, width=3, **kwds)
        # set up my docstring
        self.__doc__ = "spacecraft id"
        # all done
        return


# end of file
