# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre

# the stock recruiter; not re-exported by {pyre.nexus}, so reach into the package
from pyre.nexus.Forkserver import Forkserver as forkserver

# my preferred transport
from pyre.ipc.Sockets import Sockets


# the recruiter that asks a clean helper process for crew members
class Forkserver(forkserver, family="qed.nexus.recruiters.forkserver"):
    """
    A recruiter whose crew members are forked by a helper process spawned from the command line
    of the application, so they inherit nothing the server did after it started, e.g. the
    threads of the libraries that read products in buckets; it manages its crews over the
    socket transport, so the team can ship open file descriptors to them
    """

    # user configurable state
    channels = pyre.ipc.transport(default=Sockets)
    channels.doc = "the ipc mechanism that connects the team to its crew members"


# end of file
