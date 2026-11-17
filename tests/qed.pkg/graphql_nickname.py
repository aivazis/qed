#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the name graphql suggests for a new reader follows the product family and is not
held by any top-level entry of the configuration store
"""

# externals
import json

# support
from pyre.http.Request import Request
import journal
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store and the graphql resolver
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# the qed http server, which is never activated here, so it binds no port
server = qed.nexus.server(name="qed.test.server")


def ask(query: str) -> dict:
    """
    Resolve {query} the way the server does, and hand back its decoded answer
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
    # decode the answer and hand it off
    return json.loads(response.value)


def suggest(uri: str, module: str) -> str:
    """
    Ask for a name for the reader of {uri} in the style of the family in {module}
    """
    # assemble the query
    query = f'query {{ nickname(archive: "file:/", uri: "{uri}", module: "{module}") }}'
    # ask it
    document = ask(query)
    # the answer does not complain
    assert "errors" not in document, document
    # extract the suggestion
    return document["data"]["nickname"]


# the granule of a NISAR product
granule = (
    "NISAR_L2_PR_GSLC_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)
# is named by the NISAR conventions
assert suggest(uri=f"file:/data/{granule}.h5", module="qed.readers.nisar") == (
    "gslc-005_003_A_028-P00410"
)
# but the families without conventions of their own name it after its file
assert suggest(uri=f"file:/data/{granule}.h5", module="qed.readers.native") == granule

# a name nobody holds is suggested as is
assert suggest(uri="file:/data/vacant.bin", module="qed.readers.native") == "vacant"

# a reader that holds a name
held = qed.readers.native.flat(
    name="raster", uri="file:/data/raster.bin", shape=(4, 4), cell="complex64"
)
# makes the suggestion step aside
assert suggest(uri="file:/data/raster.bin", module="qed.readers.native") == "raster-2"

# so does configuration filed under a name, even with no component behind it
app.pyre_nameserver["settings.color"] = "blue"
assert suggest(uri="file:/data/settings.bin", module="qed.readers.native") == "settings-2"
# and the counter keeps going until it finds a free name
app.pyre_nameserver["settings-2.color"] = "red"
assert suggest(uri="file:/data/settings.bin", module="qed.readers.native") == "settings-3"

# but a name that only starts like a held one is free
assert suggest(uri="file:/data/rast.bin", module="qed.readers.native") == "rast"

# a family that is not there is a bug that trips a firewall, and the failed query is reported
# too; silence both, so the reports do not end up in the output of the test
journal.firewall("qed.gql.nickname").deactivate()
journal.warning("qed.ux.graphql").deactivate()
# ask on behalf of a family that does not exist
document = ask(
    'query { nickname(archive: "file:/", uri: "file:/data/raster.bin", module: "qed.nowhere") }'
)
# the answer carries an error for the client to show
assert document.get("errors"), document


# end of file
