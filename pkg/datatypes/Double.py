# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# my base class
from .Real import Real


# a double precision floating point number
class Double(Real, family="qed.datatypes.real64"):
    """
    The specification for double precision floating point numbers
    """

    # size
    bytes = 8


# end of file
