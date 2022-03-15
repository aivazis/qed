# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# my base class
from .Datatype import Datatype


# a complex number implemented as a pair of floats
class Complex(Datatype):
    """
    The base specification for complex numbers
    """

    # configurable state
    channels = qed.properties.strings()
    channels.default = ["complex", "amplitude", "phase", "real", "imaginary"]
    channels.doc = "the names of channels provided by complex datatypes"


    # constants
    headers = "real", "imaginary"


# end of file
