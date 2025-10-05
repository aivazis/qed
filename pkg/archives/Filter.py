# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# the base filter for selecting archive contents
class Filter(
    qed.component,
    family="qed.archives.filters.base",
    implements=qed.protocols.archiveFilter,
):
    """
    The base filter
    """

    # interface
    @qed.export
    def filter(self, archive, **kwds):
        """
        Apply the filter to a search
        """
        # ask the archive to identify itself and invoke my associated handler
        return archive.identify(archive=self, **kwds)

    # visitor support
    def onArchive(self, visitor, **kwds):
        """
        Apply my filter to a generic archive
        """
        # i don't really know how to do anything, but make sure i'm iterable because that's what
        # clients expect
        return ()


# end of file
