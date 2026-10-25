#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the query of an earth access archive reaches the client the way the archive holds it,
and that reconfiguring the archive replaces the whole query, keeping its name and its location:
a constraint the new query leaves out is cleared

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched; nothing here runs a query
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "archive_reconfigure_earth_ws")
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
# and the execution context the handlers build for every request
context = {"store": store}

# an archive of the granules of a collection within a bounding box
archive = qed.archives.earth(
    name="earth:gcov",
    uri="earth:gcov",
    collection="NISAR_L2_GCOV_BETA_V1",
    count=10,
    bbox=(-120.0, 33.0, -117.0, 35.0),
)
# connected
store.connectArchive(archive=archive)

# the query the client reads
read = """
query {
    qed {
        archives {
            name
            uri
            earth {
                collection conceptId pattern count begin end bbox point circle line polygon
            }
        }
    }
}
"""
# run it
result = qed.gql.schema.execute(read, context=context)
# it worked
assert result.errors is None, result.errors
# find the archive
shown = {entry["name"]: entry for entry in result.data["qed"]["archives"]}
# its query reaches the client as the archive holds it
assert shown["earth:gcov"]["earth"] == {
    "collection": "NISAR_L2_GCOV_BETA_V1",
    "conceptId": None,
    "pattern": None,
    "count": 10,
    "begin": None,
    "end": None,
    "bbox": [-120.0, 33.0, -117.0, 35.0],
    "point": None,
    "circle": None,
    "line": None,
    "polygon": None,
}, shown["earth:gcov"]["earth"]
# and the other kinds have none
assert shown["local:workspace"]["earth"] is None

# the mutation the form sends
reconfigure = """
mutation ($input: ReconfigureEarthAccessArchiveInput!) {
    reconfigureEarthAccessArchive(input: $input) {
        archive { name uri dirty }
    }
}
"""
# a new query: another collection, around a point, with no cap and no bounding box
payload = {
    "name": "earth:gcov",
    "uri": "earth:gcov",
    "count": "",
    "collection": {"shortName": "NISAR_L2_GUNW_BETA_V1", "conceptId": ""},
    "filters": ["geo"],
    "geo": "point",
    "point": {"longitude": "-118.5", "latitude": "34.25"},
}
# send it
result = qed.gql.schema.execute(reconfigure, context=context, variables={"input": payload})
# it worked
assert result.errors is None, result.errors
# the archive keeps its name and its location, and needs saving
assert result.data["reconfigureEarthAccessArchive"]["archive"] == {
    "name": "earth:gcov",
    "uri": "earth:gcov",
    "dirty": True,
}, result.data
# it is the same archive
assert store.archive(uri="earth:gcov") is archive
# with the new collection
assert archive.collection == "NISAR_L2_GUNW_BETA_V1", archive.collection
# around the point
assert tuple(archive.point) == (-118.5, 34.25), archive.point
# and without the constraints the new query left out
assert archive.bbox is None and archive.count is None, (archive.bbox, archive.count)


# end of file
