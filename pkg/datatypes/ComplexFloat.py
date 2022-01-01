# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# my base class
from .Complex import Complex


# a complex number implemented as a pair of floats
class ComplexFloat(Complex, family="qed.datatypes.complex4"):
    """
    The specification for complex numbers that are implemented as a pair of single precision
    floating point numbers
    """


# end of file
