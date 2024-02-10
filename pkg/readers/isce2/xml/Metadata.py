# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import pyre


# the product metadata
class Metadata(pyre.component, family="qed.readers.isce2.metadata"):
    """
    The collection of product metadata
    """

    # properties
    product = pyre.properties.str(default=None)
    description = pyre.properties.str(default=None)
    width = pyre.properties.int(default=None)
    height = pyre.properties.int(default=None)
    bands = pyre.properties.int(default=None)
    interleaving = pyre.properties.str(default=None)
    type = pyre.properties.str(default=None)
    endian = pyre.properties.str(default=None)

    # the isce2 version
    version = pyre.properties.str(default=None)


# end of file
