# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .RestoreArchivesInput import RestoreArchivesInput

# the result types
from .Archive import Archive


# bring back the trees of the connected archives
class RestoreArchives(graphene.Mutation):
    """
    List the folders of the connected archives that are on display but have nothing to show,
    e.g. the ones an earlier session recorded as expanded
    """

    # inputs
    class Arguments:
        # the request payload
        input = RestoreArchivesInput(required=True)

    # the result is the connected archives, whose trees are on their way back
    archives = graphene.List(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Bring back the trees of the connected archives
        """
        # get the store
        store = info.context["store"]
        # ask it to do the work; it returns at once when the listings run on a crew, and the
        # trees fill in as they land, each one announced to the clients
        store.restoreArchives()
        # form the mutation resolution context
        context = {"archives": list(store.archives)}
        # and resolve the mutation
        return context


# end of file
