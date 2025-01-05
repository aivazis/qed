# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# my base class
from .Datatype import Datatype


# base type for real numbers
class Real(Datatype):
    """
    The base specification for real numbers
    """

    # configurable state
    channels = qed.properties.strings()
    channels.default = ["value", "abs"]
    channels.doc = "the names of channels provided by real datatypes"


# end of file
