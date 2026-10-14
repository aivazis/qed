# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# one thing a product says about what it holds
class FlowFact(graphene.ObjectType):
    """
    One thing a product says about what it holds, as a name and a value in words
    """

    # the fields
    # what it is about
    name = graphene.String(required=True)
    # and what it says
    value = graphene.String(required=True)


# end of file
