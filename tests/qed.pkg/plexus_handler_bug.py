#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a bug in a handler of the web server stops it when the firewall that reports it is
fatal, fails only its request when it is not, and that a handler that refuses a request reaches
the client with its refusal
"""

# externals
import types

# support
import journal
import qed
from pyre.http import exceptions, responses

# a stand-in for the server: it names itself and knows the http exceptions and responses
server = types.SimpleNamespace(name="qed.test", exceptions=exceptions, responses=responses)
# and one for the request
request = types.SimpleNamespace(command="GET", url="/graphql")


# a stand-in for the dispatcher, whose handler raises {failure}
def dispatcher(failure):
    """
    Build a dispatcher whose handler raises {failure}
    """

    # the handler
    def dispatch(plexus, server, request):
        """
        Handle the request by raising {failure}
        """
        # raise it
        raise failure

    # wrap it up
    return types.SimpleNamespace(dispatch=dispatch)


# respond to a request whose handler raises {failure}
def respond(failure):
    """
    Respond to a request whose handler raises {failure}
    """
    # an application with that dispatcher
    plexus = types.SimpleNamespace(ux=dispatcher(failure=failure))
    # hand it the request
    return qed.shells.qed.pyre_respond(plexus, server=server, request=request)


# keep the reports of the bugs out of the output of the test
journal.quiet()
# the firewall that reports bugs in handlers
firewall = journal.firewall("qed.ux.handler")

# a bug, with the firewall fatal, as it is by default
try:
    # trip it
    respond(failure=KeyError("tile"))
# the firewall stops the application
except journal.FirewallError:
    # as it should
    pass
# otherwise
else:
    # the bug went unnoticed
    assert False, "a fatal firewall let the server carry on"

# make the firewall non-fatal
firewall.fatal = False
# the bug again
response = respond(failure=KeyError("tile"))
# fails only its request
assert isinstance(response, responses.InternalServerError), response

# a handler that refuses a request
try:
    # refuses it
    respond(failure=responses.NotFound(server=server))
# with a response
except responses.NotFound:
    # that reaches the server untouched
    pass
# otherwise
else:
    # the refusal was swallowed
    assert False, "a refusal did not reach the server"


# end of file
