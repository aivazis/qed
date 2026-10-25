# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the access settings
from .CredentialsInput import CredentialsInput


# the request payload for reconfiguring a data archive
class ReconfigureArchiveInput(graphene.InputObjectType):
    """
    The payload to point a connected data archive at a new location
    """

    # the uri of the archive, as it is now
    uri = graphene.String(required=True)
    # the location it moves to
    location = graphene.String(required=True)
    # its name, which, when it differs from the current one, makes a new archive take its place
    name = graphene.String()
    # the settings that say how to get at it; an empty value clears a setting
    credentials = CredentialsInput()


# end of file
