#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a graphql request whose body arrives in more than one chunk is decoded whole: the
chunks are contiguous slices of the payload and must be joined without separators, or a
query that spans a segment boundary carries a stray byte inside its string and cannot be
parsed. A body that spans segments is the norm over a network and never happens on a local
connection, which is why this needs a test
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
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# a stand-in for the http server: the responses need its name and the document factories
server = types.SimpleNamespace(
    name="qed.test", documents=pyre.http.documents, responses=pyre.http.responses
)

# the request the client sends
body = json.dumps({"query": "query { version { major minor micro } }", "variables": {}}).encode()
# with its headers
head = b"POST /graphql HTTP/1.1\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n" % (
    len(body)
)
# the bytes on the wire
raw = head + body
# split inside the string literal that holds the query
cut = len(head) + body.index(b"version") + 3

# feed the request the way the server does, one chunk at a time
request = Request()
# the first chunk carries the headers and the beginning of the body, so the request is not
# complete yet
assert not request.extract(server=server, chunk=raw[:cut])
# the second completes it
assert request.extract(server=server, chunk=raw[cut:])
# the payload arrived in two pieces
assert len(request.payload) == 2

# resolve the request
response = ux.gql.respond(store=ux.store, server=server, request=request)
# the response is a json document
document = json.loads(response.value)
# that answers the query
assert "errors" not in document, document
assert set(document["data"]["version"]) == {"major", "minor", "micro"}


# end of file
