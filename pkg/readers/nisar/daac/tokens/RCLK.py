# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Timestamp import Timestamp


# the timestamps read from the radar clock
class RCLK(Timestamp):
    """
    A time on the radar clock, in UTC; my subclasses say what it marks
    """

    # properties
    @property
    def doc(self):
        """
        Build my docstring
        """
        # fold my name in
        return f"the {self.name} time on the radar clock"


# end of file
