# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .WorkspaceProduct import WorkspaceProduct


# the workspace of the server
class Workspace(graphene.ObjectType):
    """
    The directory the server keeps what it derives in, and what it holds
    """

    # where it is
    path = graphene.String(required=True)
    # what it holds
    products = graphene.List(graphene.NonNull(WorkspaceProduct), required=True)


# end of file
