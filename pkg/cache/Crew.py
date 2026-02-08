# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed


# protocols
from .Skill import Skill


# an application that manages a skilled worker
class Crew(qed.application, family="qed.apps.crew"):
    """
    An application that manages a skilled worker on behalf of a remote process
    """

    # user configurable state
    # the badge number; set the default to {None} to trigger an error if uninitialized
    badge = qed.properties.int()
    badge.default = None
    badge.doc = "my unique badge number"

    # the communication channel with the remote process
    steward = qed.properties.tuple(schema=qed.properties.int())
    steward.doc = (
        "the pair of file descriptors that define my communication channel "
        "to the remote task manager"
    )

    # the event loop
    nexus = qed.nexus.nexus()
    nexus.doc = "the event loop manager"

    # my skill set
    worker = Skill()
    worker.doc = "the specific capabilities of this crew member"

    # the main entry point
    @qed.implements
    def main(self, *args, **kwds):
        """
        The main entry point
        """
        # grab the file descriptors for communicating with my steward
        steward = self.steward
        # if we don't have a viable pair
        if not steward:
            # show the help screen
            self.help()
            # and bail with an error code
            return 1
        # otherwise, turn the file descriptor pair into a channel
        steward = qed.ipc.pipe(descriptors=steward)
        # activate my worker
        self.activate(steward=steward)

        # get my event loop
        nexus = self.nexus
        # and start watching for events
        nexus.run(app=self)
        # close the channel
        steward.close()
        # all done
        return 0

    # implementation details
    def activate(self, steward, **kwds):
        """
        Check in with my task manager and start accepting tasks
        """
        # grab my nexus
        nexus = self.nexus
        # get the dispatcher
        dispatcher = nexus.dispatcher
        # call {process} when my {steward} endpoint is ready
        dispatcher.whenWriteReady(channel=steward, call=self.hello)
        # all done
        return 0

    def hello(self, channel, **kwds):
        """
        Register with my steward
        """
        # make a message
        message = f"hello from {self.badge}!"
        # get my nexus
        nexus = self.nexus
        # ask it for its marshaler
        marshaler = nexus.marshaler
        # send the message
        marshaler.send(channel=channel, item=message.encode())
        # ask to not get rescheduled
        return False


# end of file
