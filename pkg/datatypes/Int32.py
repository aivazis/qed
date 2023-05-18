# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# my base class
from .Integer import Integer


# a 32 bit integer
class Int32(Integer, family="qed.datatypes.int32"):
    """
    The specification for four byte integers
    """


# end of file
