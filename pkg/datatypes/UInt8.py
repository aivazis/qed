# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# my base class
from .Integer import Integer


# a 16 bit unsigned integer
class UInt8(Integer, family="qed.datatypes.uint8"):
    """
    The specification for one byte unsigned integers
    """


# end of file
