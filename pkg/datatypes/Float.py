# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# my base class
from .Real import Real


# a single precision floating point number
class Float(Real, family="qed.datatypes.real32"):
    """
    The specification for single precision floating point numbers
    """

    # the pyre memory cell name
    cell = "float32"

    # size
    bytes = 4


# end of file
