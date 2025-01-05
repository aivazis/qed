# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# my base class
from .Integer import Integer


# a 64 bit unsigned integer
class UInt64(Integer, family="qed.datatypes.uint64"):
    """
    The specification for eight byte unsigned integers
    """

    # size
    bytes = 8


# end of file
