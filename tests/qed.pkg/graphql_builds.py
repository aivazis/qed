#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the preparation of a dataset is visible through graphql under {server.builds}: its
status and times, the build of each raster behind it, and a depth and reach that are those of
its shallowest raster
"""

# externals
import json
import types

# support
import pyre
import pyre.http.documents
import pyre.http.responses
from pyre.http.Request import Request
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store and the graphql resolver
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# a stand-in for the http server: the responses need its name and the document factories
server = types.SimpleNamespace(
    name="qed.test", documents=pyre.http.documents, responses=pyre.http.responses
)


# a build that describes itself without building anything
class Built:
    """
    A stand-in for a build, with a fixed description
    """

    # meta-methods
    def __init__(self, **description):
        # save the description
        self.description = description
        # all done
        return

    # interface
    def describe(self):
        """
        Describe the build
        """
        # as told
        return self.description


# the record of a dataset whose covariance is deeper along than its mask
record = qed.ux.preparation(name="gcov.L.B.HHHH")
# with the builds of its two rasters
record.builds = [
    Built(raster="gcov.L.B.HHHH", depth=5, reach=3, level=4, runs=12, outstanding=7, fetched=90),
    Built(
        raster="gcov.L.B.HHHH.mask", depth=5, reach=2, level=3, runs=48, outstanding=40, fetched=35
    ),
]
# far enough along to render by
record.seed()
# file it where the store keeps such records
ux.store._preparations[record.name] = record


def ask(query):
    """
    Resolve {query} the way the server does, and hand back its data
    """
    # the request body
    body = json.dumps({"query": query, "variables": {}}).encode()
    # with its headers
    head = (
        b"POST /graphql HTTP/1.1\r\nContent-Type: application/json\r\n"
        b"Content-Length: %d\r\n\r\n" % len(body)
    )
    # feed it to a request
    request = Request()
    assert request.extract(server=server, chunk=head + body)
    # resolve it
    response = ux.gql.respond(store=ux.store, server=server, request=request)
    # decode the answer
    document = json.loads(response.value)
    # which must not complain
    assert "errors" not in document, document
    # hand off the data
    return document["data"]


# ask for the builds
data = ask(
    "query { server { builds { dataset status error started seeded finished depth reach "
    "rasters { raster depth reach level runs outstanding fetched } } } }"
)
# there is one
builds = data["server"]["builds"]
assert len(builds) == 1, builds
# unpack it
build = builds[0]
# it is the dataset of the record
assert build["dataset"] == "gcov.L.B.HHHH"
# seeded, and not finished
assert build["status"] == "seeded" and build["error"] is None
assert build["started"] <= build["seeded"] and build["finished"] is None
# as deep as its rasters, and available only as deep as the shallower of them
assert build["depth"] == 5 and build["reach"] == 2
# with both rasters described as they describe themselves
assert [raster["raster"] for raster in build["rasters"]] == [
    "gcov.L.B.HHHH",
    "gcov.L.B.HHHH.mask",
]
assert build["rasters"][1] == {
    "raster": "gcov.L.B.HHHH.mask",
    "depth": 5,
    "reach": 2,
    "level": 3,
    "runs": 48,
    "outstanding": 40,
    "fetched": 35,
}

# once the work is over
record.succeed()
# the build says so
build = ask("query { server { builds { status finished } } }")["server"]["builds"][0]
assert build["status"] == "ready" and build["finished"] is not None


# end of file
