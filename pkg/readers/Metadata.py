# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import pyre


# the product metadata
class Metadata(pyre.component, family="qed.readers.isce2.metadata"):
    """
    The collection of product metadata
    """

    # properties
    # the name of the dataset
    uri = pyre.properties.uri(default=None)
    # type and description
    product = pyre.properties.str(default=None)
    description = pyre.properties.str(default=None)
    # the uri of the companion file with the metadata
    aux = pyre.properties.uri(default=None)
    # product size in bytes
    bytes = pyre.properties.int(default=None)
    # shape
    width = pyre.properties.int(default=None)
    height = pyre.properties.int(default=None)
    # number of bands
    bands = pyre.properties.int(default=None)
    # the interleaving scheme
    interleaving = pyre.properties.str(default=None)
    # the cell type
    type = pyre.properties.str(default=None)
    # the encoding scheme
    endian = pyre.properties.str(default=None)

    # the product version
    version = pyre.properties.str(default=None)
    # the product specification version
    spec = pyre.properties.str(default=None)


# end of file
