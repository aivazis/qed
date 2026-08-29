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
        # hand the sources to their crews for first contact; surveyable products return
        # immediately, leaving the event loop free while their teams do the opening, and
        # a source whose survey is already under way is left alone, so staging is
        # idempotent. the outcome arrives later and reaches the client over the event
        # stream, as either {ready} with datasets or {failed} with the reason retained
        store.stage(name=name)
        # resolve the mutation with the catalog as it stands right now
        return {"readers": list(store.sources)}


# end of file
