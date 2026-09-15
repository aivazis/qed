# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Single import Single

# parts
from . import tokens


# the SME2 product descriptor
class SME2(Single, family="qed.readers.nisar.daac.sme2"):
    """
    The SME2 product descriptor
    """

    # constants
    stage = "L3"

    # my tokens
    product = tokens.product(product="SME2")
    level = tokens.level(level=3)


# end of file
