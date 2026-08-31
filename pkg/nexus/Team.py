# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
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
        # both outcomes, so the requester hydrates and settles the lifecycle itself
        super().collect(task=task, result=result)
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
            f"registered={len(self.registered)} vigils={len(self.vigils)}"
        )

    # private data
    cache = None  # the shared tile cache, attached by the fleet that builds me
    stats = None  # the statistics sink, attached by the fleet that builds me


# end of file
