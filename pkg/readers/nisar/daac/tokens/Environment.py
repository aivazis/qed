# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Token import Token


# the environment, the first letter of the CRID: the venue the product was made in
class Environment(Token, qed.properties.str):
    """
    The environment the product was made in: a single capital letter or digit

    Section 4.1 of D-102255 defines the meaning of some of the letters; the others are user
    extensions, which are in use and are accepted as they are
    """

    # constants
    # the environments the naming conventions define, by their letter
    documented = {
        "A": "ADT",
        "D": "development",
        "P": "production",
        "T": "integration and test",
        "S": "science on-demand",
        "R": "reprocessing",
    }
    # what an environment the naming conventions do not define is called
    extension = "user extension"

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # any capital letter or digit
        return rf"(?P<{self.name}>[A-Z0-9])"

    # interface
    def describe(self, value):
        """
        The meaning of the environment {value}, or "user extension" for one the naming conventions
        do not define
        """
        # look it up
        return self.documented.get(value, self.extension)

    def documents(self, value):
        """
        Check whether the naming conventions define the environment {value}
        """
        # easy enough
        return value in self.documented

    # metamethods
    def __init__(self, default="A", **kwds):
        # chain up
        super().__init__(default=default, **kwds)
        # accept a single capital letter or digit
        self.validators.append(qed.constraints.isLike(regexp=r"[A-Z0-9]$"))
        # set up my docstring
        self.__doc__ = "environment"
        # all done
        return


# end of file
