# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewChannelSetInput import ViewChannelSetInput

# the result types
from .View import View


# set the channel displayed in a view
class ViewChannelSet(graphene.Mutation):
    """
    Set the channel displayed in a view
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewChannelSetInput(required=True)

    # the result is the affected views
    views = graphene.List(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Set the channel {input.value} of the reader {input.reader} in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to set the channel
        views = store.channelSet(
            viewport=input.viewport, source=input.reader, tag=input.value
        )
        # form the mutation resolution context
        context = {"views": views}
        # and resolve the mutation
        return context


# end of file
