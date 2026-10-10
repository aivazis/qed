# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from ...Channel import Channel as Base


# the base of the channels of the native readers
class Channel(Base):
    """
    The base class for the channels of the native readers
    """

    # interface
    def iterators(self, source, origin, shape, stride, **kwds):
        """
        Render the tile of {source} at {origin}+{shape}, at the given {stride}, with the fused
        iterators of the native channels
        """
        # look for the tile maker in {libqed}
        pipeline = getattr(qed.libqed.native.channels, self.tag)
        # build the visualization pipeline and return it
        return pipeline(source=source.data, origin=origin, shape=shape, stride=stride, **kwds)


# end of file
