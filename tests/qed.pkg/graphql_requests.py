#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the tile requests of the server are visible through graphql under {server.requests}:
the zooms they arrived at, and how the recent ones were served, with their wall times
"""

# externals
import json

# support
import journal
from pyre.http.Request import Request
import qed

# the app complains about the missing web assets; this driver is not the app
journal.warning("qed.cli").deactivate()

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# the qed http server, which is never activated here, so it binds no port
server = qed.nexus.server(name="qed.test.server")
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# point the view of viewport 0 at the reader
ux.store.selectSource(viewport=0, name="d16")
# and at its amplitude; the store hands back the views it touched as it goes
for _ in ux.store.channelSet(viewport=0, source="d16", tag="amplitude"):
    # and there is nothing to do with them
    pass


def request(text):
    """
    Assemble the request {text} the way the server receives it
    """
    # make a request
    request = Request()
    # feed it the bytes
    assert request.extract(server=server, chunk=text.encode())
    # and hand it off
    return request


def ask(query):
    """
    Resolve {query} the way the server does, and hand back its data
    """
    # the request body
    body = json.dumps({"query": query, "variables": {}})
    # with its headers
    text = (
        "POST /graphql HTTP/1.1\r\nContent-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n\r\n{body}"
    )
    # resolve it
    response = ux.gql.respond(store=ux.store, server=server, request=request(text))
    # decode the answer
    document = json.loads(response.value)
    # which must not complain
    assert "errors" not in document, document
    # hand off the data
    return document["data"]


# the question
query = "query { server { requests { waiting oldest zooms { vertical horizontal count } "
query += "tiles { via count median p95 } } } }"

# before any tiles, there is nothing to report
requests = ask(query)["server"]["requests"]
assert requests == {"waiting": 0, "oldest": 0, "zooms": [], "tiles": []}, requests

# three tiles at full resolution, and one at zoom one
for zoom, origin in (("0x0", "0x0"), ("0x0", "0x32"), ("0x0", "32x0"), ("1x1", "0x0")):
    # ask for the tile
    response = ux.dispatch(
        plexus=app,
        server=server,
        request=request(f"GET /data/0/d16.data/amplitude/{zoom}/{origin}+32x32 HTTP/1.1\r\n\r\n"),
    )
    # which is rendered on the spot, since there is no fleet
    assert response.code == 200, response

# now
requests = ask(query)["server"]["requests"]
# nothing is waiting
assert requests["waiting"] == 0 and requests["oldest"] == 0
# the tiles arrived at two zooms
assert requests["zooms"] == [
    {"vertical": 0, "horizontal": 0, "count": 3},
    {"vertical": 1, "horizontal": 1, "count": 1},
], requests["zooms"]
# and were all rendered on the spot
tiles = requests["tiles"]
assert [tally["via"] for tally in tiles] == ["inline"] and tiles[0]["count"] == 4, tiles
# each of them taking some time
assert 0 < tiles[0]["median"] <= tiles[0]["p95"], tiles


# end of file
