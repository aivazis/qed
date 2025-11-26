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

    # the resolvers
    @staticmethod
    def resolve_name(credential, *_):
        """
        Get the {credential} name
        """
        # the name is the first value of the pair
        return credential[0]

    @staticmethod
    def resolve_value(credential, *_):
        """
        Get the {credential} value
        """
        # the value is the second value of the pair
        return credential[1]


# end of file
