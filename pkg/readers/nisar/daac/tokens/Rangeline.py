# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .RCLK import RCLK


# the times of rangelines
class Rangeline(RCLK):
    """
    The time on the radar clock when the instrument transmitted a rangeline
    """

    # properties
    @property
    def doc(self):
        """
        Build my docstring
        """
        # fold my name in
        return f"the {self.name} rangeline time on the radar clock"


# end of file
