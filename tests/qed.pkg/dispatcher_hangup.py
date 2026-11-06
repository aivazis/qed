#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the dispatcher hangs up on a request whose url it doesn't recognize, the kind network
scanners send, and that it leaves the server standing
"""

# externals
import types

# support
import qed
from pyre.http import responses

# a stand-in for the server: it names itself and knows the http responses
server = types.SimpleNamespace(name="qed.test", responses=responses)
# the dispatcher; routing a url needs none of the state its constructor builds
dispatcher = qed.ux.dispatcher.__new__(qed.ux.dispatcher)

# the urls that do not start with a slash, seen in scans of the server
urls = [
    # targets that are not paths
    "login?hsgid=00000000-0000-0000-0000-000000000000&hasFP=1",
    "*",
    # a proxy request
    "example.com:443",
    # a url in absolute form
    "http://example.com/",
]
# go through them
for url in urls:
    # for each method a scanner uses
    for command in ["GET", "POST", "CONNECT"]:
        # make the request
        request = types.SimpleNamespace(command=command, url=url)
        # dispatch it
        response = dispatcher.dispatch(plexus=None, server=server, request=request)
        # the dispatcher hangs up
        assert isinstance(response, responses.NoResponse), (command, url, response)


# end of file
