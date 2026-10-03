#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check how the dispatcher answers a tile request whose crew member failed: a task that ran out
of time, or failed for any other benign reason, is answered with a 503 so the client may ask
again, and is never rendered in the server; a task that took its crew member down is refused
"""

# externals
import types

# support
import journal
import pyre
import qed


# the parked response of a tile request
class Deferred:
    """
    A stand-in for the placeholder that parks a client connection
    """

    # interface
    def resolve(self, response):
        """
        Record the {response}
        """
        # file it
        self.response = response
        # and hand it back
        return response


# deliver the outcome of a tile task the way the fleet does
def deliver(error: Exception) -> tuple:
    """
    Hand {error} to the dispatcher's delivery callback and collect what it did
    """
    # a stand-in for the dispatcher with no inline renderer, so any attempt to render in the
    # server fails loudly
    dispatcher = types.SimpleNamespace()
    # a stand-in for the server that knows the http responses, and the name they carry
    server = types.SimpleNamespace(name="qed.test.server", responses=pyre.http.responses)
    # the parked response
    deferred = Deferred()
    # the tally of outcomes
    tally = []
    # deliver the outcome
    qed.ux.dispatcher._dataDeliver(
        dispatcher,
        result=None,
        error=error,
        server=server,
        deferred=deferred,
        viewport=0,
        datasetName="rslc.L.B.VV",
        channelName="amplitude",
        zoomSpec="4x4",
        zoom=(4, 4),
        spec="0x0+512x398",
        origin=(0, 0),
        shape=(512, 398),
        record=lambda code, via: tally.append((code, via)),
    )
    # hand off the response and the tally
    return deferred.response, tally


# send the warnings to the trash, so they do not end up in the output of the test
journal.warning("qed.nexus.tiles").device = journal.trash()

# a crew member that ran out of time
response, tally = deliver(error=pyre.nexus.exceptions.RecoverableError(description="took too long"))
# leaves the client free to ask again
assert response.code == 503, response.code
# and the tally says the crew handled it
assert tally == [(503, "crew")], tally

# a crew member that died
response, tally = deliver(error=pyre.nexus.exceptions.Casualty(description="crew 1 died"))
# is refused
assert response.code == 404, response.code
# and the tally says so
assert tally == [(404, "crew")], tally


# end of file
