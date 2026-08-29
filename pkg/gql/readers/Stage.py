# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .StageInput import StageInput

# the result types
from .Reader import Reader


# initiate first contact with connected data sources
class Stage(graphene.Mutation):
    """
    Stage connected data sources: establish first contact with their products so their
    datasets, selectors, and availability become known
    """

    # inputs
    class Arguments:
        # the request payload
        input = StageInput(required=True)

    # the result is the catalog of surviving readers
    readers = graphene.List(Reader)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Establish first contact with the connected sources that have not yet made it
        """
        # get the store
        store = info.context["store"]
        # unpack the optional target; a trivial value means the whole catalog
        name = input.get("reader") or None
        # initiate first contact; sources that have already made it return immediately,
        # so staging is idempotent, and casualties are disconnected with a warning
        store.open(name=name)
        # resolve the mutation with the catalog of survivors
        return {"readers": list(store.sources)}


# end of file
