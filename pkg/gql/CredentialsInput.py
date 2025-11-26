# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my parts
from .CredentialInput import CredentialInput


# the credentials payload
class CredentialsInput(graphene.InputObjectType):
    """
    The credentials payload
    """

    # the fields
    tokens = graphene.List(CredentialInput)


# end of file
