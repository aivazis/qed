# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# my base class
from .Integer import Integer


# a 16 bit integer
class Int8(Integer, family="qed.datatypes.int8"):
    """
    The specification for one byte integers
    """

    # size
    bytes = 1


# end of file
