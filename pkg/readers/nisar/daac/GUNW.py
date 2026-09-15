# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Pair import Pair

# parts
from . import tokens


# the GUNW product descriptor
class GUNW(Pair, family="qed.readers.nisar.daac.gunw"):
    """
    The GUNW product descriptor
    """

    # constants
    stage = "L2"

    # my tokens
    product = tokens.product(product="GUNW")
    level = tokens.level(level=2)


# end of file
