# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the marker the marshaler raises when its peer dies mid-conversation
from pyre.ipc.exceptions import EndOfStream

# the stock crew member; not re-exported by {pyre.nexus}, so reach into the package
from pyre.nexus.Crew import Crew as crew

# the parking place for rendered payloads
from .Spool import Spool

# the marker for tasks that took their crew member down
from .exceptions import Casualty


# the tile rendering crew member
class Crew(crew, family="qed.nexus.crews.tile"):
    """
    A crew member that renders tiles

    On the worker side, it maintains a registry of open readers so file handles are owned by
    this process and reused across tiles; on the team side, it delivers task outcomes to the
    team instead of discarding them, and treats a broken channel at every stage of its
    lifecycle as the death of its twin
    """

    # interface - worker side
    def engage(self, task, **kwds):
        """
        Carry out {task}, granting it access to my reader registry
        """
        # execute the task with my open readers on hand
        return task(readers=self.readers, **kwds)

    def perform(self, channel, **kwds):
        """
        Pick up the next task, winding down quietly if the team is gone
        """
        # my recruiter closes the stray channel copies, so a hard team death reaches me as
        # end-of-file, which the marshaler trips over while unpacking the message
        try:
            # carry on as usual
            return super().perform(channel=channel, **kwds)
        # if the channel delivered a truncated message
        except EndOfStream:
            # the team is gone; wind down my event loop
            self.stop()
            # and stop listening
            return False

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
    def activate(self, channel, team):
        """
        My worker twin is reporting ready to work, unless it died before checking in
        """
        # carefully, since the member may have died before its registration arrived
        try:
            # get the status of my twin
            status = self.marshaler.recv(channel=channel)
        # if the channel delivered a truncated message, the member is gone
        except EndOfStream:
            # clean up after it; a replacement gets recruited
            team.bury(crew=self)
            # and stop listening
            return False
        # if all is good
        if status is self.crewcodes.healthy:
            # let the team know
            team.activate(crew=self)
            # and add me to the execution schedule
            team.schedule(crew=self)
        # otherwise
        else:
            # the member is compromised; clean up, and let a replacement take its place
            team.bury(crew=self)
        # this handler is one-shot
        return False

    def assess(self, channel, team, task, **kwds):
        """
        Harvest the completion report of {task} and deliver its outcome to the {team}
        """
        # carefully, since the member may have died mid-task instead of reporting
        try:
            # grab the report
            memberstatus, taskstatus, result = self.marshaler.recv(channel=channel)
        # if the channel delivered a truncated message, the member is gone
        except EndOfStream:
            # deliver the bad news for the task it was carrying
            team.abandon(
                task=task,
                error=Casualty(description=f"crew {self.pid} died"),
            )
            # clean up after the member
            team.bury(crew=self)
            # and stop listening
            return False
        # a spooled result is just a size so far; its payload descriptor follows the report
        if isinstance(result, Spool):
            # receive it
            _, descriptors = channel.recvDescriptors(limit=1)
            # if the member died between the report and the descriptor
            if not descriptors:
                # deliver the bad news for the task it was carrying
                team.abandon(
                    task=task,
                    error=Casualty(description=f"crew {self.pid} died"),
                )
                # clean up after the member
                team.bury(crew=self)
                # and stop listening
                return False
            # otherwise, attach the payload
            result.adopt(descriptor=descriptors[0])
        # if the task ran to completion
        if taskstatus is self.taskcodes.completed:
            # deliver the tile
            team.collect(task=task, result=result)
        # otherwise
        else:
            # deliver the bad news; tiles are not retried, the client can always re-ask
            team.abandon(task=task, error=result)
        # if i'm still healthy
        if memberstatus is self.crewcodes.healthy:
            # put me back on the schedule
            team.schedule(crew=self)
        # otherwise
        else:
            # report the damage
            self.reportUnrecoverableError(team=team, task=task, error=result)
            # and take me out of the rotation
            team.dismiss(crew=self)
        # this handler is one-shot; scheduling decides my fate
        return False

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the worker side registry of open readers, keyed by the team side reader name
        self.readers = {}
        # all done
        return


# end of file
