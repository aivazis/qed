# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for saving an archive
class PersistArchiveInput(graphene.InputObjectType):
    """
    The payload for saving an archive
    """

    # the uri of the archive to save
    uri = graphene.String(required=True)


# end of file
