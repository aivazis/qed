# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my node type
from .Reader import Reader


# a reader connection
class ReaderConnection(graphene.relay.Connection):
    """
    A customized connection to a list of dataset readers
    """

    # {graphene} metadata
    class Meta:
        # register my node type
        node = Reader

    # my extra fields
    count = graphene.Int()

    # resolvers
    def resolve_count(connection, info, *_):
        """
        Count the number of readers
        """
        # get the store
        store = info.context["store"]
        # get the number of registered {readers}
        return len(store.readers)


# end of file
