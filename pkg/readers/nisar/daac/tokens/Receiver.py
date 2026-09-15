# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Numeric import Numeric


# the receiver id
class Receiver(Numeric):
    """
    The receiver id
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # form the recognizer
        return rf"R(?P<{self.name}>\d\d)"

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # ask my superclass to generate
        gid = super().gid(descriptor=descriptor)
        # add my prefix and render
        return f"R{gid}"

    # metamethods
    def __init__(self, default=0, **kwds):
        # chain up
        super().__init__(default=default, low=0, high=100, width=2, **kwds)
        # set up my docstring
        self.__doc__ = "receiver id"
        # all done
        return


# end of file
