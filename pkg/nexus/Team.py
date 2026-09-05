# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal
import pyre

# the standing team of persistent workers; not re-exported by {pyre.nexus} as a class, so
# reach into the package
from pyre.nexus.Staff import Staff

# my crew members
from .Crew import Crew

# the parking place for rendered payloads
from .Spool import Spool

# my recruiter
from .Fork import Fork


# the tile rendering team
class Team(Staff, family="qed.nexus.teams.tile"):
    """
    A standing team of persistent worker processes that render tiles

    All the machinery is inherited: the {Staff} parks idle members, notices and replaces
    casualties, and delivers task outcomes to per-task callbacks; this flavor contributes the
    crew members that render tiles and the socket transport that lets payload descriptors
    travel between the processes
    """

    # types
    # my members render tiles
    crew = Crew

    # user configurable state
    size = pyre.properties.int(default=4)
    size.doc = "the number of crew members to recruit"

    recruiter = pyre.nexus.recruiter(default=Fork)
    recruiter.doc = "the strategy for recruiting crew members"

    # implementation details
    def collect(self, task, result):
        """
        Deliver the {result} of {task} and settle the ownership of its payload
        """
        # chain up to deliver the result to every subscriber; each maps its own view. a
        # discovery record needs nothing further here: the callback of a survey carries
        # both outcomes, so the requester hydrates and settles the lifecycle itself. this
        # runs inside the harvest of the member that did the work, so a subscriber that
        # fails must not take the member with it: an exception that escapes here unwinds
        # through the event loop's dispatch, which has already taken the member's handler
        # off its registry and never puts it back, and a member nobody listens to while it
        # is counted as busy is a team that never hands out work again
        try:
            # deliver
            super().collect(task=task, result=result)
        # a subscriber that runs out of descriptors, e.g. mapping the payload, is the known
        # way this fails
        except OSError as error:
            # make a channel
            channel = journal.warning("qed.nexus.crew")
            # complain
            channel.line(f"a subscriber to {task} failed while taking delivery")
            channel.line(f"got: {error}")
            channel.line(f"the member is fine; the remaining subscribers were not served")
            # flush
            channel.log()
        # if the result is spooled
        if isinstance(result, Spool):
            # if the worker took a statistical sample and a sink is attached
            if result.stats is not None and self.stats is not None:
                # hand over the record so it accumulates into whole-dataset statistics
                self.stats(task=task, record=result.stats)
            # everybody has been served, including the case where every subscriber withdrew;
            # if a cache is attached
            if self.cache is not None:
                # it takes ownership of the payload, so identical requests become hits
                self.cache.insert(task=task, spool=result)
            # otherwise
            else:
                # release the spool so the kernel reclaims the payload
                result.close()
        # all done
        return self

    def census(self) -> str:
        """
        Report what my roster and my schedule are doing, in one line

        This is the answer to "the tiles stopped and nobody is working": a workplan that does
        not drain while every member sits on the bench means the work was never handed out,
        and a workplan that is empty while every member is marked busy means the results were
        never harvested. Neither is visible from anywhere else
        """
        # the schedule, the ledger of who is waiting for what, and the roster in its three
        # states: checking in, on a task, and parked on the bench
        return (
            f"queued={len(self.workplan)} pending={len(self.pending)} "
            f"active={len(self.active)} idle={len(self.idle)} "
            f"registered={len(self.registered)} vigils={len(self.vigils)} "
            f"deaf={self._deaf()} waking={self._waking()}"
        )

    # private data
    # implementation details
    def _deaf(self) -> int:
        """
        Count the members on a task or on the bench whose channel nobody is listening to

        A member reports on its channel, and the report is read only if the event loop
        holds a read handler for that channel: the harvester while the member is on a task,
        the death watch while it is parked. A member with neither is deaf: whatever it says
        next is never heard, and if it is counted as busy the work behind it never moves.
        This reaches into the loop's registry, which is the only place the fact exists
        """
        # the loop
        dispatcher = self.dispatcher
        # a team without one has nobody to listen anyway
        if dispatcher is None:
            # so say so
            return 0
        # the read registrations, by channel
        listening = getattr(dispatcher, "_read", None)
        # a loop that keeps them some other way cannot be asked
        if listening is None:
            # so report nothing
            return 0
        # count the members nobody listens to; a member without a channel is not a member
        # anybody could listen to, and does not count
        return sum(
            1
            for crew in set(self.active) | set(self.idle)
            if crew.channel is not None and not listening.get(crew.channel.inbound)
        )

    def _waking(self) -> int:
        """
        Count the members with a wake-up pending: a write handler the loop will call to hand
        them their next task
        """
        # the loop
        dispatcher = self.dispatcher
        # the write registrations, by channel
        pending = getattr(dispatcher, "_write", None) if dispatcher is not None else None
        # a loop that cannot be asked reports nothing
        if pending is None:
            # so say so
            return 0
        # count the members with a wake-up pending
        return sum(
            1
            for crew in set(self.active) | set(self.idle)
            if crew.channel is not None and pending.get(crew.channel.outbound)
        )

    # constants
    cache = None  # the shared tile cache, attached by the fleet that builds me
    stats = None  # the statistics sink, attached by the fleet that builds me


# end of file
