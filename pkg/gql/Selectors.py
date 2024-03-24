# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene


# my node type
class Selectors(graphene.ObjectType):
    """
    A dataset reader
    """

    # my fields
    name = graphene.String()
    values = graphene.List(graphene.String)

    # the resolvers
    @staticmethod
    def resolve_name(selector, *_):
        """
        Get the {selector} name
        """
        # the name is the first element of the pair
        return selector[0]

    @staticmethod
    def resolve_values(selector, *_):
        """
        Get the allowed {selector} values
        """
        # the value is the second element of the pair
        return selector[1]


# end of file
