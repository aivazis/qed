# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for expanding a folder
class ExpandFolderInput(graphene.InputObjectType):
    """
    The payload for expanding a folder
    """

    # the uri of the archive
    archive = graphene.String(required=True)
    # the uri of the folder to expand
    uri = graphene.String(required=True)


# end of file
