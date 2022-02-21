# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the RSLC reader
class RSLC(qed.nisar.readers.rslc, family="qed.asar.readers.rslc"):
    """
    The reader of ASAR RSLC files
    """


    # constants
    # ASAR RSLC files are marked as such
    DATASET = "/science/LSAR/RSLC/swaths/frequency{freq}/{pol}"
    POLS = "/science/LSAR/RSLC/swaths/frequency{freq}/listOfPolarizations"


# end of file
