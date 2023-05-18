# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# superclass
from .. import nisar


# the RSLC reader
class RSLC(nisar.rslc, family="qed.readers.asar.rslc"):
    """
    The reader of ASAR RSLC files
    """


# end of file
