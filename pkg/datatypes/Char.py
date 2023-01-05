# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# my base class
from .Integer import Integer


# a complex number implemented as a pair of floats
class Char(Integer, family="qed.datatypes.Char"):
    """
    The specification for one byte integers
    """


# end of file
