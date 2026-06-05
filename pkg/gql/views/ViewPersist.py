# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# persist the current reader configuration; this mutation takes no input
class ViewPersist(graphene.Mutation):
    """
    Persist the current reader configuration
    """

    # the result is the store id
    id = graphene.ID()

    # the mutator
    @staticmethod
    def mutate(root, info):
        """
        Dump the store to its persistent backing
        """
        # get the store
        store = info.context["store"]
        # ask it to persist itself
        store.pyre_dump()
        # and resolve the mutation with the store id
        return store.pyre_name


# end of file
