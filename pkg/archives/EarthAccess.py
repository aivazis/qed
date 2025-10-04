# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# an earth access data archive
class EarthAccess(
    qed.component, family="qed.archives.earth", implements=qed.protocols.archive
):
    """
    A data archive that consists of datasets available through earth access
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="earth", address=())
    uri.doc = "the archive identifier"

    filters = qed.properties.list(schema=qed.protocols.archiveFilter())
    filters.doc = "the collection of search filters to apply when looking for datasets"

    # constants
    readers = ("nisar",)

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve the archive contents at {uri}, a location expected to belong within the archive
        document space
        """
        # nothing, for now
        return []

    # hooks
    @classmethod
    def isSupported(cls):
        """
        Check whether there is runtime support for this archive type
        """
        # attempt to
        try:
            # access the external packages we need
            import earthaccess
        # if anything goes wrong
        except ImportError as error:
            # no dice
            return False
        # otherwise, chances are good there is runtime support
        return True

    # constants
    tag = "earth"
    label = "earth-access"


# end of file
