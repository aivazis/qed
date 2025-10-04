# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# framework
import qed


# protocol for data archives
class ArchiveFilter(qed.protocol, family="qed.archives.filters"):
    """
    The protocol for {qed} data archive filters
    """

    # interface requirements
    @qed.provides
    def filter(self, **kwds):
        """
        Apply the filter to a dataset search
        """


# end of file
