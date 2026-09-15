# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Token import Token


# literal text
class Literal(Token, qed.properties.str):
    """
    A literal token
    """

    # my text
    lexeme = "unknown"

    # properties
    @property
    def lexer(self):
        """
        The text i match
        """
        # easy enough
        return self.lexeme

    # interface
    def gid(self, **kwds):
        """
        Render my value in a format suitable for forming a granule id
        """
        # the default is to do nothing special
        return self.lexeme


# end of file
