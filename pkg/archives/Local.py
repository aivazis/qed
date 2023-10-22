# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed


# a local data archive
class Local(
    qed.component, family="qed.archives.local", implements=qed.protocols.archive
):
    """
    A data archive that resides on local disk
    """

    # the location
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"


# end of file
