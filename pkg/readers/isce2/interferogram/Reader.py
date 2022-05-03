# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# superclass
from ... import native


# interferograms are flat complex dataset
# with a line of amplitudes, followed by a line of phases
class Reader(native.flat, family="qed.readers.isce2.int"):
    """
    The interferogram reader
    """


# end of file
