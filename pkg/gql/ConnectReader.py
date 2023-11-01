# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene
import journal
import qed

# the result types
from .Reader import Reader


# add a new data reader to the pile
class ConnectReader(graphene.Mutation):
    """
    Connect a new data reader
    """

    # inputs
    class Arguments:
        # the update context
        name = graphene.String(required=True)
        uri = graphene.String(required=True)

    # the result is always a reader
    reader = graphene.Field(Reader)

    # the range controller mutator
    def mutate(root, info, name, uri):
        """
        Add a new reader to the pile
        """
        # make a resolution context
        context = {}
        # and resolve the mutation
        return context


# end of file
