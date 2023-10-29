# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene


# the payload for a request to add a data archive to the pile
class ConnectArchiveInput(graphene.InputObjectType):
    """
    The payload for an archive connection request
    """

    # the fields
    uri = graphene.String()


# end of file
