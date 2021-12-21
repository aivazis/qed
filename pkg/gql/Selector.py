# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


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
    def resolve_name(selector, *_):
        """
        Get the {selector} name
        """
        # ask relay
        return selector[0]


    def resolve_value(selector, *_):
        """
        Get the {selector} value
        """
        # ask
        return selector[1]


# end of file
