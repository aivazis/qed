# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# my base class
from .Integer import Integer


# a complex number implemented as a pair of floats
class Int32(Integer, family="qed.datatypes.int32"):
    """
    The specification for four byte integers
    """


# end of file
