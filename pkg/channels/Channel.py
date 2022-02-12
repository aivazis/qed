# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# a channel is visualization workflow
class Channel(qed.flow.dynamic, implements=qed.protocols.channel):
    """
    The base class for all channels
    """


    # interface
    def tile(self, source, zoom, origin, shape):
        """
        Generate a tile of the given characteristics
        """
        # get my name
        channel = self.tag
        # get the source data type
        dtype = source.cell.tag
        # splice them together
        name = f"{channel}{dtype}"

        # look for the tile maker in {libqed}
        tileMaker = getattr(qed.libqed.channels, name)

        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape2D(shape=shape)
        # and the origin into a {pyre::grid::index_t}
        origin = qed.libpyre.grid.Index2D(index=origin)

        # ask it to make a tile and return it
        return tileMaker(source=source.data, zoom=zoom, origin=origin, shape=shape)


# end of file
