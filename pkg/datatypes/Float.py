# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# my base class
from .Real import Real


# a complex number implemented as a pair of floats
class Float(Real, family="qed.datatypes.real4"):
    """
    The specification for single precision floating point numbers
    """


# end of file
