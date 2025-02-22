# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# my base class
from .Integer import Integer


# a single byte integer
class Char(Integer, family="qed.datatypes.Char"):
    """
    The specification for one byte integers
    """

    # size
    bytes = 1


# end of file
