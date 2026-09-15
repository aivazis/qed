# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Pair import Pair

# parts
from . import tokens


# the RIFG product descriptor
class RIFG(Pair, family="qed.readers.nisar.daac.rifg"):
    """
    The RIFG product descriptor
    """

    # constants
    stage = "L1"

    # my tokens
    product = tokens.product(product="RIFG")


# end of file
