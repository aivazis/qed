# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the RSLC reader; RSLCs contain one {complex64} dataset
class RSLC(qed.readers.native.flat, family="qed.isce2.readers.rslc"):
    """
    The reader of RSLC files
    """


    # public data
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"


# end of file
