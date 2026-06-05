# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for collapsing a viewport
class ViewCollapseInput(graphene.InputObjectType):
    """
    The payload for removing a view from the pile
    """

    # the viewport to collapse
    viewport = graphene.Int(required=True)


# end of file
