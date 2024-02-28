# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# my base class
from .Integer import Integer


# a 16 bit integer
class Int16(Integer, family="qed.datatypes.int16"):
    """
    The specification for two byte integers
    """

    # size
    bytes = 2


# end of file
