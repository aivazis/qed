#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the workspace of the server is visible through graphql under {server.workspace}:
where it is, and the data derived from each product, measured by the blocks that were written
"""

# externals
import json
import os
import shutil

# support
import pyre
from pyre.http.Request import Request
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store and the graphql resolver
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# the qed http server, which is never activated here, so it binds no port
server = qed.nexus.server(name="qed.test.server")

# the scratch area that stands in for the workspace
scratch = pyre.primitives.path(__file__).parent / "graphql_workspace.scratch"
# start clean
if scratch.exists():
    shutil.rmtree(str(scratch))
scratch.mkdir()
# point the workspace at it
app.workspace.path = str(scratch)


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


# the question
query = "query { server { workspace { path products { kind name bytes } } } }"

# an empty workspace
workspace = ask(query)["server"]["workspace"]
# is where it was put, and holds nothing
assert workspace["path"] == str(scratch) and workspace["products"] == [], workspace

# the levels of a product: a sparse level, sized far beyond what was written into it
home = scratch / ".qed" / "pyramids" / "GRANULE" / "L" / "A" / "HH"
home.mkdir(parents=True)
with open(str(home / "level-01.tiles"), "wb") as level:
    # a large hole
    level.truncate(64 * 2**20)
    # and a little data at the start
    level.write(b"\x01" * 4096)
# and a small sidecar
with open(str(home / "pyramid.json"), "w") as sidecar:
    sidecar.write("{}")

# the product is there
products = ask(query)["server"]["workspace"]["products"]
assert [(product["kind"], product["name"]) for product in products] == [
    ("pyramids", "GRANULE")
], products
# measured by the blocks that were written, which is far less than the size of its files
written = products[0]["bytes"]
assert 0 < written < 2**20, written
# and exactly what the system says they occupy
assert written == sum(
    os.stat(str(home / name)).st_blocks * 512 for name in ("level-01.tiles", "pyramid.json")
)

# clean up
shutil.rmtree(str(scratch))


# end of file
