# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a factory the palette offers
class CatalogEntry(graphene.ObjectType):
    """
    A factory that can be placed on a pipeline diagram
    """

    # the fields
    # the family of the factory, which is how a client asks for one
    family = graphene.String(required=True)
    # its short name
    name = graphene.String(required=True)
    # its documentation
    doc = graphene.String()
    # the names of its input and output slots, in the order it declares them
    inputs = graphene.List(graphene.NonNull(graphene.String), required=True)
    outputs = graphene.List(graphene.NonNull(graphene.String), required=True)


# end of file
