# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a factory's refusal to make one of its products
class FlowRefusal(graphene.ObjectType):
    """
    A factory's refusal to make one of its products: which one, and why, kept apart so whoever
    shows them can put them in words
    """

    # the fields
    # the name of the slot of the product the factory would not make
    product = graphene.String(required=True)
    # and why
    reason = graphene.String(required=True)


# end of file
