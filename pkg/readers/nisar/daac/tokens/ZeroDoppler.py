# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .RCLK import RCLK


# the times of data processed as zero doppler
class ZeroDoppler(RCLK):
    """
    A time on the radar clock that marks data processed as zero doppler
    """

    # properties
    @property
    def doc(self):
        """
        Build my docstring
        """
        # fold my name in
        return f"the {self.name} zero doppler time on the radar clock"


# end of file
