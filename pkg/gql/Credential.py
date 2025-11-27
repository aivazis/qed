# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# my node type
class Credential(graphene.ObjectType):
    """
    A binding of the name of a credential token to its value
    """

    # my fields
    name = graphene.String()
    value = graphene.String()


# end of file
