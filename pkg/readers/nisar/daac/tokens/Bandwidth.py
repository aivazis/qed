# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Discrete import Discrete


# the bandwidth
class Bandwidth(Discrete, qed.properties.int):
    """
    The bandwidth
    """

    # the allowed values
    allowed = (0, 5, 20, 40, 77)

    # properties
    def doc(self):
        """
        Set up my docstring
        """
        # fold my name and return
        return self.name

    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # build the recognizer
        recognizer = "|".join(f"{value:02}" for value in self.allowed)
        # and form the recognizer
        return rf"(?P<{self.name}>{recognizer})"

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # get my value
        value = getattr(descriptor, self.name)
        # and render
        return f"{value:02}"

    # metamethods
    def __init__(self, allowed=allowed, **kwds):
        # chain up
        super().__init__(default=allowed[0], allowed=allowed, **kwds)
        # {eval} fails on expressions where integers have leading zeroes, so strip them
        self.converters.append(lambda value, **kwds: int(value))
        # all done
        return


# end of file
