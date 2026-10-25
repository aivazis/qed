# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the payload of a connection, whose fields this one repeats
from .ConnectEarthAccessArchiveInput import ConnectEarthAccessArchiveInput


# the request payload for reconfiguring an earth access archive
class ReconfigureEarthAccessArchiveInput(ConnectEarthAccessArchiveInput):
    """
    The payload to replace the query of a connected earth access archive: the fields of a
    connection, where {uri} names the archive, which keeps its name and its location
    """


# end of file
