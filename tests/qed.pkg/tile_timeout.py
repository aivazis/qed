#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check how the dispatcher answers a tile request whose crew member failed: a task that ran out
of time, or failed for any other benign reason, is answered with a 503 so the client may ask
again, and is never rendered in the server; a task that took its crew member down is refused,
and remembered as a suspect so it is never handed to another crew member
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


# the fleet that routed the task
class Fleet:
    """
    A stand-in for the fleet that only remembers its suspect tasks
    """

    # interface
    def suspect(self, task):
        """
        Remember {task} as a suspect
        """
        # add it to the pile
        self.suspects.add(task)
        # and hand me back
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # start with no suspects
        self.suspects = set()
        # all done
        return


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
    # the fleet that routed the task
    fleet = Fleet()
    # the tally of outcomes
    tally = []
    # deliver the outcome
    qed.ux.dispatcher._dataDeliver(
        dispatcher,
        result=None,
        error=error,
        server=server,
        deferred=deferred,
        fleet=fleet,
        task="the task",
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
    # hand off the response, the tally, and the suspects
    return deferred.response, tally, fleet.suspects


# send the warnings to the trash, so they do not end up in the output of the test
journal.warning("qed.nexus.tiles").device = journal.trash()

# a crew member that ran out of time
response, tally, suspects = deliver(
    error=pyre.nexus.exceptions.RecoverableError(description="took too long")
)
# leaves the client free to ask again
assert response.code == 503, response.code
# the tally says the crew handled it
assert tally == [(503, "crew")], tally
# and the task is not a suspect
assert suspects == set(), suspects

# a crew member that died
response, tally, suspects = deliver(error=pyre.nexus.exceptions.Casualty(description="crew 1 died"))
# is refused
assert response.code == 404, response.code
# the tally says so
assert tally == [(404, "crew")], tally
# and the task is remembered as a suspect
assert suspects == {"the task"}, suspects


# end of file
