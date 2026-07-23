# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# a channel is visualization workflow
class Channel(qed.flow.dynamic, implements=qed.protocols.channel):
    """
    The base class for all channels
    """

    # constants
    tag = None

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # nothing to do
        return

    def controllers(self):
        """
        Generate the set of controllers that can manipulate my state
        """
        # by default, nothing
        return []

    def eval(self, pixel):
        """
        Extract the channel value from a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'rep'")

    def project(self, pixel):
        """
        Compute the channel representation of a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'rep'")

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # get my name
        name = self.tag
        # look for the tile maker in {libqed}
        pipeline = getattr(qed.libqed.native.channels, name)

        # turn the zoom levels into per-axis strides
        stride = tuple(2**level for level in zoom)
        # build the visualization pipeline and return it
        return pipeline(
            source=source.data, origin=origin, shape=shape, stride=stride, **kwds
        )

    def update(self, **kwds):
        """
        Update the state of one of my controllers
        """
        # nothing for me to do
        return {}


# end of file
