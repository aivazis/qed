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
        name = type(self).__name__
        # look for my bindings in {libqed}
        factory = getattr(qed.libqed.channels, name)
        # instantiate the workflow
        channel = factory()
        # ask it to make a tile and return it
        return channel.tile(source=source, zoom=zoom, origin=origin, shape=shape)


# end of file
