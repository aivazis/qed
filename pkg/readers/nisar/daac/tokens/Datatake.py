# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .RCLK import RCLK


# the times of datatakes
class Datatake(RCLK):
    """
    A time on the radar clock read from the pre-take or the post-take of a datatake
    """

    # properties
    @property
    def doc(self):
        """
        Build my docstring
        """
        # fold my name in
        return f"the {self.name} datatake time on the radar clock"


# end of file
