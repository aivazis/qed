# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# my base class
from .Integer import Integer


# a single byte integer
class Char(Integer, family="qed.datatypes.Char"):
    """
    The specification for one byte integers
    """

    # the pyre memory cell name
    cell = "int8"

    # size
    bytes = 1


# end of file
