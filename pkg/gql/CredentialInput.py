# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the payload for credential token
class CredentialInput(graphene.InputObjectType):
    """
    The payload for a credential token
    """

    # the fields
    name = graphene.String(required=True)
    value = graphene.String(required=True)


# end of file
