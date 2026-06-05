# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for setting the channel displayed in a view
class ViewChannelSetInput(graphene.InputObjectType):
    """
    The payload for setting the channel displayed in a view
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the reader whose channel is being set
    reader = graphene.String(required=True)
    # the channel tag
    value = graphene.String(required=True)


# end of file
