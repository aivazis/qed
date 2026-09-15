# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .RefreshArchiveInput import RefreshArchiveInput

# the result types
from .Archive import Archive


# list every folder on display again
class RefreshArchive(graphene.Mutation):
    """
    List every folder on display again
    """

    # inputs
    class Arguments:
        # the request payload
        input = RefreshArchiveInput(required=True)

    # the result is the archive whose tree moved
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Refresh the archive at {input.uri}
        """
        # get the store
        store = info.context["store"]
        # ask it to do the work
        archive = store.refreshArchive(uri=input.uri)
        # form the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
