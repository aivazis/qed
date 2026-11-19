# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the stock crew member; re-exported by {pyre.nexus} since the persistent-team graduation
from pyre.nexus.Crew import Crew as crew


# the tile rendering crew member
class Crew(crew, family="qed.nexus.crews.tile"):
    """
    A crew member that renders tiles

    The lifecycle machinery is inherited, including the delivery of rendered payloads, which
    travel inside the completion report as channels over their spool files; this flavor
    contributes the worker side reader registry, so file handles are owned by the worker and
    reused across tiles
    """

    # interface - worker side
    def engage(self, task, **kwds):
        """
        Carry out {task}, granting it access to my reader registry
        """
        # execute the task with my open readers and mounted archives on hand
        return task(readers=self.readers, archives=self.archives, **kwds)

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the worker side registry of open readers, keyed by the team side reader name
        self.readers = {}
        # the worker side registry of mounted archives, keyed by the team side archive name
        self.archives = {}
        # all done
        return


# end of file
