# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# a complex number implemented as a pair of floats
class Datatype(qed.flow.product, implements=qed.protocols.datatype):
    """
    The base class for all datatypes
    """

    # configurable state
    byteswap = qed.properties.bool(default=False)
    byteswap.doc = "control whether byte swapping is necessary"

    channels = qed.properties.strings()
    channels.doc = "the names of channels provided by this datatype"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.default = 512,512
    tile.doc = "the preferred shape of dataset subsets"


# end of file
