# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for disconnecting a data archive
class DisconnectArchiveInput(graphene.InputObjectType):
    """
    The payload to disconnect a data archive
    """

    # the uri of the archive to disconnect
    uri = graphene.String(required=True)


# end of file
