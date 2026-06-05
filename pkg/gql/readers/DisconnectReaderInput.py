# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for disconnecting a data reader
class DisconnectReaderInput(graphene.InputObjectType):
    """
    The payload to disconnect a data reader
    """

    # the name of the reader to disconnect
    name = graphene.String(required=True)


# end of file
