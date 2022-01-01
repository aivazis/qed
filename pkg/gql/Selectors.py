# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


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
    def resolve_name(selector, *_):
        """
        Get the {selector} name
        """
        # the name if the first element of the pair
        return selector[0]


    def resolve_values(selector, *_):
        """
        Get the allowed {selector} values
        """
        # the value if the second element of the pair
        return selector[1]


# end of file
