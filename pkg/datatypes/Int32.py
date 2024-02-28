# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# my base class
from .Integer import Integer


# a 32 bit integer
class Int32(Integer, family="qed.datatypes.int32"):
    """
    The specification for four byte integers
    """

    # size
    bytes = 4


# end of file
