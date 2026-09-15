# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved

# support
import qed

# superclass
from .Token import Token


# a numeric token
class Numeric(Token, qed.properties.int):
    """
    A numeric token
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # get the width
        width = self.width
        # build the recognizer
        digits = r"\d+" if width is None else r"\d" * width
        # and form the recognizer
        return rf"(?P<{self.name}>{digits})"

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # get my value
        value = getattr(descriptor, self.name)
        # and render
        return self.str(value)

    def str(self, value):
        """
        Build a string representation in normal form
        """
        # if {value} is a string
        if isinstance(value, str):
            # i have nothing to say
            return super().str(value=value)
        # otherwise, get the width
        width = self.width
        # normalize, render, and return
        return f"{value:0{width}}" if width is not None else f"{value}"

    # metamethods
    def __init__(self, low, high, width=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the allowed values
        self.low = low
        self.high = high
        # record the width
        self.width = width
        # when the width is non-trivial
        if width is not None:
            # {eval} fails on expressions where integers have leading zeroes, so strip them
            self.converters.append(lambda value, **kwds: int(value))
        # update my validators
        self.validators.append(qed.constraints.inRange(low=low, high=high))
        # all done
        return


# end of file
