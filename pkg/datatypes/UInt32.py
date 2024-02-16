# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# my base class
from .Integer import Integer


# a 32 bit unsigned integer
class UInt32(Integer, family="qed.datatypes.uint32"):
    """
    The specification for four byte unsigned integers
    """


# end of file
