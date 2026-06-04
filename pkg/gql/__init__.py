# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# query
from .Query import Query
# mutation
from .Mutation import Mutation


# build the schema
schema = graphene.Schema(
    # supported operations
    query = Query,
    mutation = Mutation,
)


# render the schema as SDL text; the single source of truth shared by the generated
# {ux/schema/qed.gql} relay artifact, the {qed-schema} exporter, and the {/schema}
# server route
def sdl() -> str:
    """
    Render the {qed} GraphQL schema as SDL text
    """
    # graphene emits canonical SDL when the schema is stringified
    return str(schema)


# end of file
