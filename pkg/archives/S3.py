# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed


# a S3 data archive
class S3(qed.component, family="qed.archives.s3", implements=qed.protocols.archive):
    """
    A data archive that resides in an S3 bucket
    """

    # the location
    uri = qed.properties.uri()
    uri.doc = "the location of the archive"


# end of file
