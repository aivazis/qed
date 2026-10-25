#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the nicknames the server suggests for new archives: a local archive is named after its
folder, an archive in a bucket after the bucket, and one of earth access granules after their
collection; a name some component holds already, including an archive that was disconnected,
is passed over for one that keeps more of the path, and once the path runs out, for a numbered
one; the characters that do not belong in a name become underscores

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "archive_nickname_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it
os.makedirs(workspace)

# the configuration file
original = (
    "# -*- pyre -*-\n\n"
    "# the installation under test has no web client; keep the complaint about it quiet\n"
    "qed.journal.warning.qed.startup.assets:\n"
    "    active: no\n\n"
    "# end of file\n"
)
# write it
with open(os.path.join(workspace, "qed.yaml"), mode="w", encoding="utf-8") as stream:
    # all at once
    stream.write(original)

# work out of the scratch workspace, so its configuration file is the one that loads
os.chdir(workspace)

# support
import qed

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store

# the kinds of archives
local = qed.archives.local
# an archive in a bucket
s3 = qed.archives.s3
# and one of earth access granules
earth = qed.archives.earth


# the suggestion for an archive of a {kind} at {uri}
def suggest(kind, uri, collection=None):
    # ask the store
    return store.archiveNickname(factory=kind, uri=uri, collection=collection)


# a local archive is named after its folder
assert suggest(local, "file:/data/nisar/gcov") == "gcov", suggest(local, "file:/data/nisar/gcov")
# once that name is held
store.connectArchive(archive=local(name="local:gcov", uri="file:/data/nisar/gcov"))
# another archive in a folder with the same name keeps more of its path
assert suggest(local, "file:/other/nisar/gcov") == "nisar_gcov", suggest(
    local, "file:/other/nisar/gcov"
)
# and more still once that is held too
store.connectArchive(archive=local(name="local:nisar_gcov", uri="file:/data/nisar/gcov/x"))
# until the whole path is in
assert suggest(local, "file:/other/nisar/gcov") == "other_nisar_gcov"
# and once that is held as well
store.connectArchive(archive=local(name="local:other_nisar_gcov", uri="file:/elsewhere"))
# it gets a number
assert suggest(local, "file:/other/nisar/gcov") == "other_nisar_gcov-2"
# the name an archive being reconfigured holds is its own to keep
assert (
    store.archiveNickname(factory=local, uri="file:/data/nisar/gcov", current="local:gcov")
    == "gcov"
)
# the root of the filesystem has no name to offer
assert suggest(local, "file:/") == ""

# an archive in a bucket is named after the bucket
uri = "s3://nisar-os-rs-pop1/products/gcov"
# without its path
assert suggest(s3, uri) == "nisar-os-rs-pop1", suggest(s3, uri)
# an archive that held that name
held = s3(name="s3:nisar-os-rs-pop1", uri=uri)
# and was connected
store.connectArchive(archive=held)
# and disconnected again
store.disconnectArchive(uri=uri)
# still holds it, since pyre would hand it back for the name; so the suggestion keeps the path,
# one folder at a time
assert suggest(s3, uri) == "nisar-os-rs-pop1_products", suggest(s3, uri)
# the dots of a bucket name become underscores
assert suggest(s3, "s3://my.bucket/data") == "my_bucket", suggest(s3, "s3://my.bucket/data")
# a name held by an archive of another kind is no obstacle
assert suggest(s3, "s3://gcov") == "gcov", suggest(s3, "s3://gcov")

# an archive of earth access granules is named after their collection
collection = "NISAR_L2_GCOV_BETA_V1"
# as it is
assert suggest(earth, "earth:", collection=collection) == collection
# and without one, there is nothing to suggest
assert suggest(earth, "earth:") == ""


# end of file
