# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# the channel ux state
class Channel(qed.protocol, family="qed.ux.channels"):
    """
    The state of a channel view
    """

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the channel view base
        return qed.ux.channel


# end of file
