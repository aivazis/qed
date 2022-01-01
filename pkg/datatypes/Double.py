# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# my base class
from .Real import Real


# a complex number implemented as a pair of floats
class Double(Real, family="qed.datatypes.real8"):
    """
    The specification for double precision floating point numbers
    """


# end of file
