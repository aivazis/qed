# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for bringing back the trees of the archives
class RestoreArchivesInput(graphene.InputObjectType):
    """
    The payload for bringing back the trees of the connected archives
    """

    # the client that is asking; the request itself needs nothing, since it concerns every
    # archive, but a payload without fields is not a payload
    client = graphene.String(required=False)


# end of file
