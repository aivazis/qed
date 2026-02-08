# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed


# an application that can farm out work to remote workers
class Bureau(qed.application, family="qed.apps.bureau"):
    """
    An application that can farm out work to a remote crew
    """

    # the event loop
    nexus = qed.nexus.nexus()
    nexus.doc = "the event loop manager"

    # the main entry point
    @qed.implements
    def main(self, *args, **kwds):
        """
        The main entry point
        """
        # there is very little to do here
        # the work order is created during the service initialization phase of whichever
        # service has work to carry out. so all that needs to happen here is to kickstart the nexus
        return self.nexus.run(app=self)


# end of file
