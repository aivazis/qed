# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .View import View


# remove a view from the pile
class Persist(graphene.Mutation):
    """
    Persist the current reader configuration
    """

    # inputs
    class Arguments:
        # the mutation context
        dummy = graphene.ID(required=False)

    # the result is the store id
    id = graphene.ID()

    # the range controller mutator
    @staticmethod
    def mutate(root, info, **kwds):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to split the view
        store.pyre_dump()
        # and resolve the mutation
        return store.pyre_name


# end of file
