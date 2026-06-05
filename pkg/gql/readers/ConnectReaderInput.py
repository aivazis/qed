# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for connecting a data reader
class ConnectReaderInput(graphene.InputObjectType):
    """
    The payload to connect a new data reader
    """

    # the archive that holds the data product
    archive = graphene.String(required=True)
    # the reader to use
    reader = graphene.String(required=True)
    # the name to give the reader
    name = graphene.String(required=True)
    # the uri of the data product
    uri = graphene.String(required=True)
    # the shape of the raster, if known
    lines = graphene.String(required=False)
    samples = graphene.String(required=False)
    # the cell type, if known
    cell = graphene.String(required=False)


# end of file
