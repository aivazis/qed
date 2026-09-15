# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Literal import Literal


# literal text
class NISAR(Literal, internal=True):
    """
    The prefix of all granule ids
    """

    # my text
    lexeme = "NISAR"
    # i don't have a match group, so hide me from the trait searches
    internal = True


# end of file
