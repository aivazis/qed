# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved

# support
import qed

# superclass
from .Token import Token


# a token with a discrete set of allowed values
class Discrete(Token):
    """
    A token with a known set of allowed values
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # splice my allowed values
        alt = "|".join(self.allowed)
        # and form the recognizer
        return rf"(?P<{self.name}>{alt})"

    # metamethods
    def __init__(self, allowed, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the allowed values
        self.allowed = allowed
        # update my validators
        self.validators.append(qed.constraints.isMember(*allowed))
        # all done
        return


# end of file
