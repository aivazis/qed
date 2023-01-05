# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed


# the base controller
class Controller(qed.component, implements=qed.protocols.controller):
    """
    The base class for controller implementations
    """


    # interface
    def autotune(self, **kwds):
        """
        Adjust my values based on a sample of my dataset
        """
        # nothing to do
        return


    # constants
    tag = "controller"


# end of file
