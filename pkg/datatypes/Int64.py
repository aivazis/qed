# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# my base class
from .Integer import Integer


# a 64 bit integer
class Int64(Integer, family="qed.datatypes.int64"):
    """
    The specification for eight byte integers
    """

    # the pyre memory cell name
    cell = "int64"

    # size
    bytes = 8


# end of file
