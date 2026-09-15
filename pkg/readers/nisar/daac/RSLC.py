# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Single import Single

# parts
from . import tokens


# the RSLC product descriptor
class RSLC(Single, family="qed.readers.nisar.daac.rslc"):
    """
    The RSLC product descriptor
    """

    # constants
    stage = "L1"

    # my tokens
    product = tokens.product(product="RSLC")


# end of file
