# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre

# the stock recruiter; not re-exported by {pyre.nexus}, so reach into the package
from pyre.nexus.Fork import Fork as fork

# my preferred transport
from pyre.ipc.Sockets import Sockets


# the tile crew recruiter
class Fork(fork, family="qed.nexus.recruiters.fork"):
    """
    A recruiter that manages its crews over the socket transport, so the team can ship open
    file descriptors to them, e.g. to delegate a client connection for a direct response
    """

    # user configurable state
    channels = pyre.ipc.transport(default=Sockets)
    channels.doc = "the ipc mechanism that connects the team to its crew members"


# end of file
