# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
import graphene

# my node type
from .Reader import Reader


# a reader connection
class ReaderConnection(graphene.relay.Connection):
    """
    A connection to a list of dataset readers
    """

    # {graphene} metadata
    class Meta:
        # register my node type
        node = Reader


# end of file
