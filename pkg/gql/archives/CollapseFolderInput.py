# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for collapsing a folder
class CollapseFolderInput(graphene.InputObjectType):
    """
    The payload for collapsing a folder
    """

    # the uri of the archive
    archive = graphene.String(required=True)
    # the uri of the folder to collapse
    uri = graphene.String(required=True)


# end of file
