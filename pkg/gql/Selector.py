# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# my node type
class Selector(graphene.ObjectType):
    """
    A binding of a dataset selector to a specific value
    """

    # my fields
    name = graphene.String()
    value = graphene.String()

    # the resolvers
    @staticmethod
    def resolve_name(selector, *_):
        """
        Get the {selector} name
        """
        # the name is the first value of the pair
        return selector[0]

    @staticmethod
    def resolve_value(selector, *_):
        """
        Get the {selector} value
        """
        # the name is the second value of the pair
        return selector[1]


# end of file
