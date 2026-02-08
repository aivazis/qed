# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the specification of worker recruitment strategies
class Recruiter(qed.protocol, family="qed.nexus.recruiters"):
    """
    The specification of worker recruitment strategies
    """

    # interface
    @qed.required
    def recruit(self, team, **kwds):
        """
        Recruit new members for the {team}
        """

    @qed.required
    def deploy(self, team, **kwds):
        """
        Create a new team member
        """

    @qed.required
    def dismiss(self, team, nember, **kwds):
        """
        The {team} manager has dismissed the given {member}
        """

    # the default implementation
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use {exec} as the default strategy for adding team members
        from .Exec import Exec

        # hand it off
        return Exec


# end of file
