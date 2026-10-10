# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from ....Channel import Channel as Base


# the base of the channels of interferograms
class Channel(Base):
    """
    The base class for the channels of isce2 interferograms
    """

    # interface
    def iterators(self, source, origin, shape, stride, **kwds):
        """
        Render the tile of {source} at {origin}+{shape}, at the given {stride}, with the fused
        iterators of the channels of interferograms
        """
        # look for the tile maker in {libqed}
        pipeline = getattr(qed.libqed.isce2.interferogram.channels, self.tag)
        # ask it to make a tile and return it
        return pipeline(source=source.data, origin=origin, shape=shape, stride=stride, **kwds)


# end of file
