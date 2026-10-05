# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .CatalogEntry import CatalogEntry


# the factories the palette offers that implement one protocol
class CatalogGroup(graphene.ObjectType):
    """
    The factories that implement one protocol, e.g. the filters or the colormaps
    """

    # the fields
    # the family of the protocol
    family = graphene.String(required=True)
    # its short name
    name = graphene.String(required=True)
    # the factories that implement it
    entries = graphene.List(graphene.NonNull(CatalogEntry), required=True)


# end of file
