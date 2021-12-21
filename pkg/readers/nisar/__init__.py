# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# support
import qed


# foundries
@qed.foundry(implements=qed.protocols.reader, tip="RSLC reader")
def rslc():
    """
    The reader of RSLC files in ISCE2 format
    """
    # get the reader
    from .RSLC import RSLC
    # and publish it
    return RSLC


# end of file
