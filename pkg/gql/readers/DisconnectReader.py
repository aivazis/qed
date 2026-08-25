# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal

# the request payload
from .DisconnectReaderInput import DisconnectReaderInput

# the result types
from .Reader import Reader


# remove a data reader from the pile
class DisconnectReader(graphene.Mutation):
    """
    Disconnect a data reader
    """

    # inputs
    class Arguments:
        # the request payload
        input = DisconnectReaderInput(required=True)

    # the result is the disconnected reader
    reader = graphene.Field(Reader)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Remove a reader from the pile
        """
        # unpack the payload
        name = input.name
        # get the store
        store = info.context["store"]
        # remove it from the pile
        reader = store.disconnectSource(name=name)
        # look for the fleet of tile rendering teams; only the qed server flavor has one
        fleet = getattr(info.context["server"], "fleet", None)
        # if there is one
        if fleet is not None:
            # disband the team dedicated to this reader, releasing its worker caches
            fleet.dismiss(reader=name)
        # form the mutation resolution context
        context = {"reader": reader}
        # and resolve the mutation
        return context


# end of file
