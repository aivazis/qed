# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .CollapseFolderInput import CollapseFolderInput

# the result types
from .Archive import Archive


# take a folder off display
class CollapseFolder(graphene.Mutation):
    """
    Take a folder off display
    """

    # inputs
    class Arguments:
        # the request payload
        input = CollapseFolderInput(required=True)

    # the result is the archive whose tree moved
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Collapse the folder at {input.uri} of the archive at {input.archive}
        """
        # get the store
        store = info.context["store"]
        # ask it to do the work
        archive = store.collapseFolder(archive=input.archive, uri=input.uri)
        # form the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
