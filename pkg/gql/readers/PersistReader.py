# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .PersistReaderInput import PersistReaderInput

# the result types
from .Reader import Reader


# write a reader into the configuration files
class PersistReader(graphene.Mutation):
    """
    Write a reader into the user's configuration files, along with the state of its controllers
    """

    # inputs
    class Arguments:
        # the request payload
        input = PersistReaderInput(required=True)

    # the result is the reader that was saved
    reader = graphene.Field(Reader)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Save the reader called {input.name}
        """
        # get the store
        store = info.context["store"]
        # ask it to do the work; this is the only thing that writes a reader into the
        # configuration, so it happens when the user asks for it and at no other time
        reader = store.persistSource(name=input.name)
        # form the mutation resolution context
        context = {"reader": reader}
        # and resolve the mutation
        return context


# end of file
