# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import socket

# support
import journal

# the marker the marshaler raises when its peer dies mid-conversation
from pyre.ipc.exceptions import EndOfStream

# the failure a task reports when it could not be carried out but the member is fine
from pyre.nexus.exceptions import RecoverableError

# the stock crew member; re-exported by {pyre.nexus} since the persistent-team graduation
from pyre.nexus.Crew import Crew as crew

# the parking place for rendered payloads
from .Spool import Spool


# the tile rendering crew member
class Crew(crew, family="qed.nexus.crews.tile"):
    """
    A crew member that renders tiles

    The lifecycle machinery is inherited; this flavor contributes the worker side reader
    registry, so file handles are owned by the worker and reused across tiles, and the spool
    protocol, which ships rendered payloads by descriptor instead of through the byte stream
    """

    # interface - worker side
    def engage(self, task, **kwds):
        """
        Carry out {task}, granting it access to my reader registry
        """
        # execute the task with my open readers on hand
        return task(readers=self.readers, **kwds)

    def report(self, channel, crewstatus, taskstatus, result, **kwds):
        """
        Post the completion report, shipping any spooled payload by descriptor
        """
        # chain up to send the standard report; a spooled result pickles as just its size
        super().report(
            channel=channel,
            crewstatus=crewstatus,
            taskstatus=taskstatus,
            result=result,
            **kwds,
        )
        # if the result is spooled
        if isinstance(result, Spool):
            # its descriptor follows the report as ancillary data
            channel.sendDescriptors(descriptors=[result.file.fileno()])
            # release my copy; the kernel keeps the payload alive for the recipient
            result.close()
        # this handler is one-shot
        return False

    # interface - team side
    def harvest(self, channel):
        """
        Extract a completion report from {channel}, collecting any spooled payload
        """
        # chain up for the report itself
        memberstatus, taskstatus, result = super().harvest(channel=channel)
        # a spooled result is just a size so far; its payload descriptor follows the report
        if isinstance(result, Spool):
            # carefully, since the descriptor lands in this process's table, and the kernel
            # refuses it when the table is full
            try:
                # receive it
                _, descriptors = channel.recvDescriptors(limit=1)
            # if the table is full
            except OSError as error:
                # the kernel dropped the descriptor but left the byte that carried it in the
                # socket, where the next report would be read from the wrong place; take
                # that byte out of the way
                self._drain(channel=channel)
                # make a channel
                warning = journal.warning("qed.nexus.crew")
                # complain, since this is how a process that has run out of descriptors
                # stops serving tiles: the render happened, and its payload cannot land
                warning.line(f"crew {self.pid}: could not receive the payload of a render")
                warning.line(f"got: {error}")
                warning.line(f"the process is probably out of file descriptors")
                # flush
                warning.log()
                # the member is fine; the task is not, and whoever asked for it is told
                return (
                    memberstatus,
                    self.taskcodes.failed,
                    RecoverableError(description=f"payload not received: {error}"),
                )
            # a missing descriptor means the member died between the report and its trailer,
            # which is a death like any other
            if not descriptors:
                # so report it as such
                raise EndOfStream(channel=channel)
            # otherwise, attach the payload
            result.adopt(descriptor=descriptors[0])
        # hand off the report
        return memberstatus, taskstatus, result

    # implementation details
    def _drain(self, channel) -> None:
        """
        Take the byte that carried a payload descriptor out of {channel}, after the kernel
        refused to deliver the descriptor itself
        """
        # carefully, since there may be nothing there after all
        try:
            # take the byte, without waiting for one
            channel.recv(1, socket.MSG_DONTWAIT)
        # nothing to take
        except OSError:
            # is fine
            pass
        # all done
        return

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the worker side registry of open readers, keyed by the team side reader name
        self.readers = {}
        # all done
        return


# end of file
