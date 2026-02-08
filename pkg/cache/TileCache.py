# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed
import journal

# superclass
from .Pool import Pool


# the manager of the local cache of dataset tiles
# given a dataset uri, cache is responsible for managing the local tile cache
class TileCache(Pool, family="qed.services.tileCache"):
    """
    The manager of the dataset tile cache
    """

    # implementation details
    # crew management
    def punchIn(self, channel, app, badge):
        """
        A crew member is reporting for duty
        """
        # chain up
        super().punchIn(app=app, channel=channel, badge=badge)
        # MGA: FIX: this is a toy response; generalize
        # get the {app} marshaller
        marshaler = app.nexus.marshaler
        # read the message
        message = marshaler.recv(channel=channel)
        # report
        print(f"from tiler: {message}")
        # don't reschedule
        return False


    def exec(self, app, badge, channel, **kwds):
        """
        Generate a crew member specification suitable for the {exec} recruiter
        """
        # build the path to my worker harness
        tiler = f"{app.pyre_home}/tiler.py"
        # and its command line
        argv = [
            # the harness is the zeroth argument, by convention
            tiler,
            # the worker badge number
            f"--badge={badge}",
            # the channel to the steward
            f"--steward={channel.inbound,channel.outbound}",
        ]
        # hand the pair off to the recruiter
        return tiler, argv


# end of file
