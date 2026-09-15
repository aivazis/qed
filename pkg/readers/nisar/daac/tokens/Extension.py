# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Literal import Literal


# literal text
class Extension(Literal):
    """
    The extension separator in the granule ids
    """

    # my lexeme
    lexeme = r"\."
    # i can't have a match group, so hide me from the trait searches
    internal = True

    # interface
    def gid(self, **kwds):
        """
        Render my value in a format suitable for forming a granule id
        """
        # can't use my {lexeme} because of the escape sequence...
        return "."


# end of file
