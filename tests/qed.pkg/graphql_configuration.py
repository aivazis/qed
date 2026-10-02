#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the configuration of the components reachable from the application is visible
through graphql under {server.configuration}: each component once, each trait with where its
value came from and the components it refers to, and no secret anywhere
"""

# externals
import json

# support
from pyre.http.Request import Request
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store and the graphql resolver
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# the qed http server, which is never activated here, so it binds no port
server = qed.nexus.server(name="qed.test.server")

# a reader with a secret in its credentials, which is never opened here
secretive = qed.readers.nisar.gslc(
    name="secretive", uri="file:nowhere.h5", credentials={"profile": "hunter2"}
)
# is one of the datasets of the application
app.datasets = list(app.datasets) + [secretive]


def ask(query):
    """
    Resolve {query} the way the server does, and hand back its answer as it went on the wire
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
    # hand off the answer
    return response.value


# ask for the configuration
wire = ask(
    "query { server { configuration { name family traits { "
    "name kind schema value secret priority locator components } } } }"
)
# the secret is nowhere in the answer
assert "hunter2" not in wire
# decode it
document = json.loads(wire)
# which does not complain
assert "errors" not in document, document
# the components
components = document["data"]["server"]["configuration"]
# the walk starts at the application
assert components[0]["name"] == app.pyre_name
# and describes every component once
names = [component["name"] for component in components]
assert len(names) == len(set(names)), names
# the traits of the application
traits = {trait["name"]: trait for trait in components[0]["traits"]}
# include its datasets, which refer to the reader
datasets = traits["datasets"]
assert "secretive" in datasets["components"], datasets
# which is described
assert "secretive" in names
# and every value says where it came from
assert all(trait["priority"] for trait in components[0]["traits"])
# the reader with the secret
reader = next(component for component in components if component["name"] == "secretive")
# has its credentials
credentials = next(trait for trait in reader["traits"] if trait["name"] == "credentials")
# marked secret, and without a value
assert credentials["secret"] is True and credentials["value"] is None
# while its address is there
uri = next(trait for trait in reader["traits"] if trait["name"] == "uri")
assert uri["secret"] is False and "nowhere.h5" in uri["value"]


# end of file
