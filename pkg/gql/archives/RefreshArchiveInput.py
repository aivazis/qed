# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for refreshing an archive
class RefreshArchiveInput(graphene.InputObjectType):
    """
    The payload for refreshing an archive
    """

    # the uri of the archive to refresh
    uri = graphene.String(required=True)


# end of file
