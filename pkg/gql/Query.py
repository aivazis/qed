# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
import graphene
# server version tag
from .Version import Version


# the query
class Query(graphene.ObjectType):
    """
    The top level query
    """

    # server version info
    version = graphene.Field(Version, required=True)


    # version
    def resolve_version(root, info):
        """
        Build and return the server version
        """
        # prep an empty context for the {version} resolution
        return {}


# end of file
