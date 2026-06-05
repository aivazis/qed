# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for splitting a viewport
class ViewSplitInput(graphene.InputObjectType):
    """
    The payload for splitting a viewport in two
    """

    # the viewport to split
    viewport = graphene.Int(required=True)


# end of file
