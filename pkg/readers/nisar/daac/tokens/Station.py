# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Token import Token


# the name of the ground station
class Station(Token, qed.properties.str):
    """
    The name of the ground station
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # form my recognizer
        return rf"(?P<{self.name}>[A-Z]+)"

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # set up my docstring
        self.__doc__ = "ground station"
        # all done
        return


# end of file
