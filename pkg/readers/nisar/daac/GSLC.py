# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Single import Single

# parts
from . import tokens


# the GSLC product descriptor
class GSLC(Single, family="qed.readers.nisar.daac.gslc"):
    """
    The GSLC product descriptor
    """

    # constants
    stage = "L2"

    # my tokens
    product = tokens.product(product="GSLC")
    level = tokens.level(level=2)


# end of file
