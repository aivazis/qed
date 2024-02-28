# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# my base class
from .Integer import Integer


# a 16 bit unsigned integer
class UInt16(Integer, family="qed.datatypes.uint16"):
    """
    The specification for two byte unsigned integers
    """

    # size
    bytes = 2


# end of file
