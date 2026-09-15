# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Pair import Pair

# parts
from . import tokens


# the GOFF product descriptor
class GOFF(Pair, family="qed.readers.nisar.daac.goff"):
    """
    The GOFF product descriptor
    """

    # constants
    stage = "L2"

    # my tokens
    product = tokens.product(product="GOFF")
    level = tokens.level(level=2)


# end of file
