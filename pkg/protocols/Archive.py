# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# framework
import qed


# protocol for data archives
class Archive(qed.protocol, family="qed.archives"):
    """
    The protocol for {qed} data archives
    """

    # the location
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    # interface
    @qed.provides
    def contents(self, uri):
        """
        Retrieve the archive contents at {uri}, a location expected to belong within the archive
        document space
        """


# end of file
