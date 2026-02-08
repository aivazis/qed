# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import qed

# my skill
from .Tiling import Tiling


# hdf5 tile fetching as a crew member's skill
class Tiler(qed.component, family="qed.crew.skills.tiler", implements=Tiling):
    """
    Tilers can extract multidimensional rectilinear subsets of hdf5 datasets
    """

    # obligations for components that implement this protocol
    @qed.implements
    def perform(self, **kwds):
        """
        Execute an assigned task that fits this skill
        """
        print(f"{self}: perform: {kwds}")
        # all done
        return self


# end of file
