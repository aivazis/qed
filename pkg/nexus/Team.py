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
        # chain up to deliver the result to every subscriber; each maps its own view
        super().collect(task=task, result=result)
        # if the result is spooled
        if isinstance(result, Spool):
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

    # private data
    cache = None  # the shared tile cache, attached by the fleet that builds me


# end of file
