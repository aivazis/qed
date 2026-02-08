# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed


# the specification of a crew member's skill set
class Skill(qed.protocol, family="qed.crew.skills"):
    """
    The specification a specialized ability of a crew member
    """

    # obligations for components that implement this protocol
    @qed.provides
    def perform(self, **kwds):
        """
        Execute an assigned task that fits this skill
        """


# end of file
