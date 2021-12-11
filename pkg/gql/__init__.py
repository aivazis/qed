# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
import graphene

# query
from .Query import Query


# build the schema
schema = graphene.Schema(
    # supported operations
    query = Query,
)


# end of file
