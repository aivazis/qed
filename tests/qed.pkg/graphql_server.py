#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the process of the server, its cache of rendered tiles, and its teams of workers are
visible through graphql under {server}, and that a server without a fleet reports neither
"""

# externals
import json
import os

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


# the question, asked twice
query = (
    "query { server { "
    "process { pid host platform cores memory started uptime descriptors ceiling beats } "
    "cache { capacity slots entries bytes hits misses } "
    "fleet { teams { name kind owner size idle active queued pending deaf waking } } "
    "} }"
)

# without a fleet
data = ask(query)["server"]
# the process describes itself
process = data["process"]
assert process["pid"] == os.getpid()
assert process["cores"] > 0 and process["memory"] > 0 and process["ceiling"] > 0
# as a server that was never activated
assert process["started"] is None and process["uptime"] == 0 and process["beats"] == 0
# the descriptors are counted wherever the platform can tell
assert process["descriptors"] is None or 0 < process["descriptors"] <= process["ceiling"]
# and there is neither a cache nor any teams to describe
assert data["cache"] is None and data["fleet"] is None

# a fleet, with an event loop of its own
fleet = qed.nexus.fleet(name="qed.test.fleet")
fleet.dispatcher = pyre.ipc.newPSL()
# which forms the team of a reader when asked for it, without recruiting anybody yet
team = fleet.team(reader="c16")
# and hands it to the store, the way the server does when it is activated
ux.store.fleet = fleet

# with the fleet
data = ask(query)["server"]
# the cache is empty, within its budgets
cache = data["cache"]
assert cache["entries"] == 0 and cache["bytes"] == 0 and cache["hits"] == 0
assert cache["capacity"] == fleet.cache.capacity and cache["slots"] == fleet.cache.limit
# and the team of the reader is there, with nothing to do
teams = data["fleet"]["teams"]
assert teams == [
    {
        "name": team.pyre_name,
        "kind": "tile",
        "owner": "c16",
        "size": team.size,
        "idle": 0,
        "active": 0,
        "queued": 0,
        "pending": 0,
        "deaf": 0,
        "waking": 0,
    }
], teams

# let the fleet go
fleet.disband()


# end of file
