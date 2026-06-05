# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the nested payload
from .CredentialsInput import CredentialsInput


# the request payload for connecting a data archive
class ConnectArchiveInput(graphene.InputObjectType):
    """
    The payload to connect a new data archive
    """

    # the archive name
    name = graphene.String(required=True)
    # the archive uri
    uri = graphene.String(required=True)
    # the access credentials, if any
    credentials = CredentialsInput()


# end of file
