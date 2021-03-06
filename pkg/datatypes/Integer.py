# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# my base class
from .Datatype import Datatype


# a complex number implemented as a pair of floats
class Integer(Datatype):
    """
    The base specification for real numbers
    """

    # configurable state
    channels = qed.properties.strings()
    channels.default = ["value", "abs"]
    channels.doc = "the names of channels provided by integer datatypes"


# end of file
