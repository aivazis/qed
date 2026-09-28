# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the data derived from one product
class WorkspaceProduct(graphene.ObjectType):
    """
    The data of one kind derived from one product, and the bytes it occupies on disk
    """

    # the kind of derived data, e.g. pyramids
    kind = graphene.String(required=True)
    # the product, by its granule id or by a digest of its address
    name = graphene.String(required=True)
    # the bytes on disk, counting only the blocks that were written
    bytes = graphene.Float(required=True)


# end of file
