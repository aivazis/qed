# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload of a connection, whose fields this one repeats
from .ConnectEarthAccessArchiveInput import ConnectEarthAccessArchiveInput


# the request payload for reconfiguring an earth access archive
class ReconfigureEarthAccessArchiveInput(ConnectEarthAccessArchiveInput):
    """
    The payload to replace the query of a connected earth access archive: the fields of a
    connection, where {uri} names the archive; a {name} that differs from the current one makes
    a new archive at {location} take its place
    """

    # the location of the archive, which is made from its name
    location = graphene.String()


# end of file
