# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for placing a reader in a viewport
class ViewReaderSelectInput(graphene.InputObjectType):
    """
    The payload for placing a reader in a viewport
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the reader to place; null clears the viewport
    reader = graphene.String(required=False)


# end of file
