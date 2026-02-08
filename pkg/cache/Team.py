# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# protocols
from .Recruiter import Recruiter


# the manager of a collection of processes that coöperate to carry out a work plan
class Team(qed.protocol, family="qed.nexus.teams"):
    """
    The specification for process collectives that coöperate to execute a work plan
    """

    # user configurable state
    size = qed.properties.int()
    size.doc = "the maximum number of team members"

    recruiter = Recruiter()
    recruiter.doc = "the strategy for recruiting new team members"

    # interface requirements
    @qed.required
    def assemble(self, workplan, **kwds):
        """
        Recruit a team to execute the set of tasks in my {workplan}
        """

    @qed.required
    def vacancies(self):
        """
        Compute how many recruits are needed to take the team to full strength
        """


# end of file
