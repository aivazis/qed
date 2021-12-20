# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
import graphene


# my node type
class SelectorDecl(graphene.ObjectType):
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
        # ask relay
        return ""


    def resolve_values(selector, *_):
        """
        Get the allowed {selector} values
        """
        # ask
        return []


# end of file
