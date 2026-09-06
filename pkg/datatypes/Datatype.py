# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import sys

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
    tile.default = 512, 512
    tile.doc = "the preferred shape of dataset subsets"

    # constants
    summary = ("value",)

    # the pyre memory cell name for this datatype; each concrete datatype sets its own, and it is
    # what {pyre.grid} wants when it lays a grid over a block of memory in the host's byte order
    cell = None
    # the size of one cell, in bytes; each concrete datatype sets its own
    bytes = None

    # the value my cells use to say "there is nothing here", or {None} when they have no way to
    # say it. this is the vocabulary the statistics kernels speak: they skip a cell whose
    # magnitude is a nan and count every other one, so a raster that can hold a nan spells
    # absence with one, and a raster that cannot has no absent cells at all
    blank = None

    @property
    def ordered(self) -> str:
        """
        The name of the pyre cell that reads my cells in place: my {cell}, with the byte order
        marker my {byteswap} calls for, so a product written on a machine of the other endianness
        comes through the swap
        """
        # cells in the host's order, and single byte cells, need no marker
        if not self.byteswap or self.bytes == 1:
            # so the plain name will do
            return self.cell
        # otherwise the cells are in the order the host lacks
        return self.cell + ("be" if sys.byteorder == "little" else "le")

    @property
    def spec(self) -> str:
        """
        My specification, in the form the datatype protocol resolves back into me: my family, led
        by the byte order marker my {byteswap} calls for
        """
        # my family
        family = self.pyre_family()
        # cells in the host's order need no marker
        if not self.byteswap:
            # so the family will do
            return family
        # otherwise, lead with the marker of the order the host lacks
        return (">" if sys.byteorder == "little" else "<") + family

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
