#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the client learns how to get at the contents of an archive, and never the secrets of
the session that does: an archive in a bucket shows its profile and its region, and a local one
shows nothing
"""

# support
import qed

# the type that presents archives to the client
from qed.gql.archives.Archive import Archive

# an archive in a bucket, with a profile and a region
bucket = qed.archives.s3(
    name="s3:access", uri="s3://bucket/products", profile="science", region="us-west-2"
)
# what the client sees about how to get in
shown = {entry["name"]: entry["value"] for entry in Archive.resolve_credentials(bucket)}
# is the profile and the region, and nothing else: no keys, no token
assert shown == {"profile": "science", "region": "us-west-2"}, shown
# and asking for them did not open a session, which would have gone looking for the keys
assert bucket._session is None

# a local archive
local = qed.archives.local(name="local:access", uri="file:/tmp")
# needs nothing to get in, so the client sees nothing
assert list(Archive.resolve_credentials(local)) == []


# end of file
