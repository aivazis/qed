# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# superclass
from .. import native


# the SLC reader; SLCs contain one {complex64} dataset
class SLC(native.flat, family="qed.readers.isce2.slc"):
    """
    The reader of SLC files
    """

    # public data
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"


# end of file
