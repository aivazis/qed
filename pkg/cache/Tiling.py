# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed

# superclass
from .Skill import Skill


# the specification of a crew member's skill set
class Tiling(Skill, family="qed.crew.skills.tiling"):
    """
    The specification of the tiling skill, i.e. the ability to extract multidimensional rectilinear
    subsets from remote datasets
    """


# end of file
