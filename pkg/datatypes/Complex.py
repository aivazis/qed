# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# my base class
from .Datatype import Datatype


# base class for complex numbers
class Complex(Datatype):
    """
    The base specification for complex numbers
    """

    # configurable state
    channels = qed.properties.strings()
    channels.default = ["complex", "amplitude", "phase", "real", "imaginary"]
    channels.doc = "the names of channels provided by complex datatypes"

    # constants
    summary = "real", "imaginary", "amplitude", "phase"


# end of file
