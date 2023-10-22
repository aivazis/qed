# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


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


# end of file
