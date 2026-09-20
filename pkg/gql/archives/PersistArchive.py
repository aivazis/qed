# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .PersistArchiveInput import PersistArchiveInput

# the result types
from .Archive import Archive


# write an archive into the configuration files
class PersistArchive(graphene.Mutation):
    """
    Write an archive into the user's configuration files, along with what it has on display
    """

    # inputs
    class Arguments:
        # the request payload
        input = PersistArchiveInput(required=True)

    # the result is the archive that was saved
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Save the archive at {input.uri}
        """
        # get the store
        store = info.context["store"]
        # ask it to do the work; this is the only thing that writes an archive into the
        # configuration, so it happens when the user asks for it and at no other time
        archive = store.persistArchive(uri=input.uri)
        # form the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
