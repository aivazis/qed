# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ExpandFolderInput import ExpandFolderInput

# the result types
from .Archive import Archive


# put a folder on display and list it
class ExpandFolder(graphene.Mutation):
    """
    Put a folder on display and list it
    """

    # inputs
    class Arguments:
        # the request payload
        input = ExpandFolderInput(required=True)

    # the result is the archive whose tree moved
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Expand the folder at {input.uri} of the archive at {input.archive}
        """
        # get the store
        store = info.context["store"]
        # ask it to do the work
        archive = store.expandFolder(archive=input.archive, uri=input.uri)
        # form the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
