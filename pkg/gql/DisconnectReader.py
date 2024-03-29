# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .Reader import Reader


# remove a data reader from the pile
class DisconnectReader(graphene.Mutation):
    """
    Disconnect a data reader
    """

    # inputs
    class Arguments:
        # the update context
        name = graphene.String(required=True)

    # the result is the disconnected reader
    reader = graphene.Field(Reader)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, name):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # remove it from the pile
        reader = store.disconnectReader(name=name)
        # form the mutation resolution context
        context = {"reader": reader}
        # and resolve the mutation
        return context


# end of file
