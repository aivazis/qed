# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import time


# the crew member registration record
class Badge:
    """
    Crew member information
    """

    # interface
    def dismiss(self):
        """
        Terminate a crew member
        """
        # mark the termination time
        self.dismissed = time.time()
        # all done

    # metamethods
    def __init__(self, app, badge, wid, channel, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the registration info
        self.eid = badge
        self.wid = wid
        self.contact = channel
        # record the start time
        self.hired = time.time()
        # no dismissal time implies an active registration
        self.dismissed = None
        # all done
        return


# end of file
