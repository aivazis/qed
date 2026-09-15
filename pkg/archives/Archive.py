# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal


# a local data archive
class Archive(qed.component, family="qed.archives.base", implements=qed.protocols.archive):
    """
    The base data archive
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    # constants
    readers = ()

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve my contents at {uri}, a location expected to belong within the archive document
        space
        """
        # i got nothing
        return []

    def credentials(self):
        """
        Generate the credentials necessary to access my contents
        """
        # nothing, by default
        return {}

    # constants
    tag = "<base>"
    label = "<base>"


# end of file
