# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Pair import Pair

# parts
from . import tokens


# the RUNW product descriptor
class RUNW(Pair, family="qed.readers.nisar.daac.runw"):
    """
    The RUNW product descriptor
    """

    # constants
    stage = "L1"

    # my tokens
    product = tokens.product(product="RUNW")


# end of file
