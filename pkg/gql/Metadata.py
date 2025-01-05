# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# information about a dataset
class Metadata(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    id = graphene.ID()
    uri = graphene.String()
    product = graphene.String()
    bytes = graphene.Float()
    cells = graphene.Float()
    shape = graphene.List(graphene.Int)

    # resolvers
    @staticmethod
    def resolve_id(context, info, **kwds):
        """
        Get the file size of a data product
        """
        # unpack my context
        uri = context["uri"]
        archive = context["archive"]
        module = context["module"]
        # use the uri as the id
        return f"{archive}:{module}:{uri}"

    @staticmethod
    def resolve_uri(context, info, **kwds):
        """
        Get the file size of a data product
        """
        # unpack my context
        uri = context["uri"]
        # and return the product uri
        return uri

    @staticmethod
    def resolve_product(context, info, **kwds):
        """
        Get the number of data cells of a product
        """
        # unpack my context
        metadata = context["metadata"]
        # if none is available
        if metadata is None:
            # bail
            return None
        # otherwise, extract the product type
        return metadata.product

    @staticmethod
    def resolve_bytes(context, info, **kwds):
        """
        Get the product size in bytes
        """
        # unpack my context
        metadata = context["metadata"]
        # if none is available
        if metadata is None:
            # bail
            return None
        # otherwise, extract the file size in bytes and return it
        return metadata.bytes

    @staticmethod
    def resolve_cells(context, info, **kwds):
        """
        Get the number of data cells of a product
        """
        # unpack my context
        metadata = context["metadata"]
        # if no metadata is available
        if metadata is None:
            # bail
            return None
        # otherwise, extract the shape
        width = metadata.width
        height = metadata.height
        # if either dimension is unknown
        if width is None or height is None:
            # bail
            return None
        # otherwise, compute the number of cells and return it
        return width * height

    @staticmethod
    def resolve_shape(context, info, **kwds):
        """
        Get the product shape as (lines, samples)
        """
        # unpack my context
        metadata = context["metadata"]
        # if no metadata is available
        if metadata is None:
            # bail
            return None
        # otherwise, extract the shape
        width = metadata.width
        height = metadata.height
        # if either dimension is unknown
        if width is None or height is None:
            # bail
            return None
        # otherwise, form the shape and return it
        return height, width


# end of file
