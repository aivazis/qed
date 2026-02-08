# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed
import journal


# the base class of service implementors
class Server(qed.component, family="qed.services.server", protocol=qed.nexus.service):
    """
    The base class for service implementers
    """

    # service obligations
    @qed.implements
    def activate(self, app, dispatcher):
        """
        Enable the tile cache as a service
        """
        # make a channel
        channel = journal.info("qed.cache.server")
        # report
        channel.log(f"{self.pyre_name}: activate")
        # all done
        return

    @qed.implements(tip="acknowledge a peer that has initiated a connection")
    def acknowledge(self, dispatcher, channel):
        """
        A peer has attempted to establish a connection
        """
        # make a channel
        channel = journal.info("qed.cache.server")
        # report
        channel.log(f"{self.pyre_name}: acknowledge")
        # all done
        return

    @qed.implements(tip="determine whether to start a conversation with the peer")
    def validate(self, channel, address):
        """
        Examine the peer {address} and determine whether to continue the conversation
        """
        # make a channel
        channel = journal.info("qed.cache.server")
        # report
        channel.log(f"{self.pyre_name}: validate")
        # all done
        return

    @qed.implements(tip="indicate interest in continuing to interact with the peer")
    def connect(self, dispatcher, channel, address):
        """
        Prepare to start accepting requests from a new peer
        """
        # make a channel
        channel = journal.info("qed.cache.server")
        # report
        channel.log(f"{self.pyre_name}: connect")
        # all done
        return

    @qed.implements(tip="try to understand and respond to the peer request")
    def process(self, dispatcher, channel):
        """
        Start or continue a conversation with a peer over {channel}
        """
        # make a channel
        channel = journal.info("qed.cache.server")
        # report
        channel.log(f"{self.pyre_name}: process")
        # all done
        return

    @qed.implements
    def shutdown(self):
        """
        Clean up and shutdown
        """
        # make a channel
        channel = journal.info("qed.cache.server")
        # report
        channel.log(f"{self.pyre_name}: shutdown")
        # all done
        return


# end of file
