# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my node type
from .Archive import Archive


# a data archive connection
class ArchiveConnection(graphene.relay.Connection):
    """
    A customized connection to a list of data archives
    """

    # {graphene} metadata
    class Meta:
        # register my node type
        node = Archive

    # my extra fields
    count = graphene.Int()

    # resolvers
    @staticmethod
    def resolve_count(connection, info, *_):
        """
        Count the number of data archives
        """
        # get the panel
        panel = info.context["panel"]
        # get the number of registered data archives
        return len(panel.archives)


# end of file
