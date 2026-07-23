# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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


    # constants
    summary = ("value",)

    # the pyre memory cell name for this datatype; each concrete datatype sets its own, and it is
    # what {pyre.grid} wants when it lays a grid over a block of memory
    cell = None


    @property
    def tag(self):
        """
        Generate my type tag
        """
        # use the class name as the tag; it is interpolated into the names of the {libqed} tile
        # generators that are specialized by cell type, e.g. {profileFloat}. the connection to
        # {pyre.grid}, on the other hand, goes through {cell}, the pyre memory cell name
        return self.__class__.__name__


# end of file
