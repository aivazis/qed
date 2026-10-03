#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the server discards a burst of tile requests as a whole once a newer one arrives: the
requests made with settings the view has since replaced are refused on arrival, and the ones still
waiting are withdrawn from the teams and answered, as soon as the first request made with the new
settings arrives
"""

# externals
import uuid

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
server = qed.nexus.server(name="qed.test.bursts")
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# point the view of viewport 0 at the reader
ux.store.selectSource(viewport=0, name="d16")
# and at its amplitude
for _ in ux.store.channelSet(viewport=0, source="d16", tag="amplitude"):
    # the views it touched are of no interest
    pass
# the view behind the requests
view = ux.store.view(viewport=0)


# a fleet that keeps track of what it is asked, and renders nothing
class Fleet:
    """
    A stand-in for the fleet of tile teams
    """

    # interface
    def suspected(self, task):
        """
        No task has ever taken a crew member down
        """
        # so none is suspect
        return False

    def lookup(self, task):
        """
        Nothing is ever in the cache
        """
        # so nothing is found
        return None

    def render(self, task, callback):
        """
        Remember a task that was queued
        """
        # file it
        self.rendered.append(task.origin)
        # all done
        return self

    def revoke(self, task, callback):
        """
        Remember a task that was withdrawn
        """
        # file it
        self.revoked.append(task.origin)
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the origins of the tiles queued and withdrawn
        self.rendered = []
        self.revoked = []
        # all done
        return


# a parked response that keeps track of how it was answered
class Parked:
    """
    A stand-in for a deferred response
    """

    # interface
    def resolve(self, response):
        """
        Remember the answer
        """
        # file it
        self.response = response
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # not answered yet
        self.response = None
        # and nobody to tell of a hangup yet
        self.abandoned = None
        # all done
        return


# give the server the stand-ins
fleet = Fleet()
server.fleet = fleet
server.deferred = Parked


def tile(origin, session):
    """
    Ask for the tile at {origin} under the settings {session}
    """
    # the request, as the client spells it
    text = f"GET /data/0/d16.data/amplitude/0x0/{origin}+16x16?session={session} HTTP/1.1\r\n\r\n"
    # make a request
    request = Request()
    # feed it the bytes
    assert request.extract(server=server, chunk=text.encode())
    # and hand it to the dispatcher
    return ux.dispatch(plexus=app, server=server, request=request)


# the settings of the view now
old = str(view.session)
# two tiles of the current burst wait for the crew
first = tile(origin="0x0", session=old)
second = tile(origin="0x16", session=old)
assert isinstance(first, Parked) and isinstance(second, Parked)
assert fleet.rendered == [(0, 0), (0, 16)]

# the settings of the view change
view.session = uuid.uuid1()
new = str(view.session)

# a straggler of the old burst is refused on arrival, without reaching the crew
late = tile(origin="16x0", session=old)
assert late.code == 410, late
assert fleet.rendered == [(0, 0), (0, 16)]
# and nothing of the old burst has been touched yet
assert first.response is None and second.response is None and fleet.revoked == []

# the first tile of the new burst
third = tile(origin="16x16", session=new)
# waits for the crew
assert isinstance(third, Parked) and third.response is None
assert fleet.rendered == [(0, 0), (0, 16), (16, 16)]
# and retires the old burst: its tiles are withdrawn from the team
assert fleet.revoked == [(0, 0), (0, 16)]
# and their connections are answered at once
assert first.response.code == 410 and second.response.code == 410

# a tile of the new burst whose client hangs up is withdrawn, as before
third.abandoned()
assert fleet.revoked == [(0, 0), (0, 16), (16, 16)]
# and leaves its burst
assert ux._bursts[0][1] == {}


# end of file
