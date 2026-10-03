#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the route that serves the spectrum of a region: it refuses requests the client should not
have made, answers a late one as gone, serves a picture it has on hand, and hands everything else
to the crews of the reader
"""

# externals
import functools
import types

# support
import journal
import pyre
import qed

# the firewall of the dispatcher reports each refusal; keep the reports out of the output, and
# let the route answer the way it does in case firewalls aren't fatal, so the answers can be seen
journal.firewall("qed.ux.dispatch").device = journal.trash()
journal.firewall("qed.ux.dispatch").fatal = False

# an RSLC reader, never opened here; the route only asks what kind of product it is
rslc = qed.readers.nisar.rslc(name="route_rslc", uri="file:/nowhere/rslc.h5")
# and a reader of another kind
gslc = qed.readers.nisar.gslc(name="route_gslc", uri="file:/nowhere/gslc.h5")
# the dataset on display, as the server knows it
dataset = types.SimpleNamespace(
    pyre_name="route_rslc.L.A.HH",
    shape=(1000, 800),
    selector={"band": "L", "frequency": "A", "polarization": "HH"},
)


# the parked response of a request
class Deferred:
    """
    A stand-in for the placeholder that parks a client connection
    """

    # the hangup hook, armed by the route
    abandoned = None


# the crews of the server
class Fleet:
    """
    A stand-in for the fleet that remembers what it was asked
    """

    # interface
    def suspected(self, task):
        """
        Check whether {task} is known to take its crew member down
        """
        # look it up
        return task in self.suspects

    def lookup(self, task):
        """
        Retrieve the cached picture of {task}, if it is on hand
        """
        # look it up
        return self.cache.get(task)

    def render(self, task, callback):
        """
        Record the {task} handed to the crews
        """
        # file it
        self.rendered.append(task)
        # all done
        return self

    def revoke(self, task, callback):
        """
        Withdraw {task}
        """
        # nothing to do
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # nothing suspect, cached, or rendered yet
        self.suspects = set()
        self.cache = {}
        self.rendered = []
        # all done
        return


# the store behind the views
class Store:
    """
    A stand-in for the store that holds a single view
    """

    # interface
    def view(self, viewport):
        """
        Retrieve the view on display in {viewport}
        """
        # there is only one
        return self.views[viewport]

    # metamethods
    def __init__(self, reader, **kwds):
        # chain up
        super().__init__(**kwds)
        # a single view of the dataset by {reader}
        view = types.SimpleNamespace(reader=reader, dataset=dataset)
        # that decides whether it has a spectrum the way the real one does
        view.spectrumLimit = functools.partial(qed.ux.view.spectrumLimit, view)
        # is all there is
        self.views = [view]
        # all done
        return


# ask for {url} with the dataset on display shown by {reader}, through {fleet}
def ask(url: str, reader=rslc, fleet=None):
    """
    Resolve {url} with the spectrum route and hand back its response
    """
    # the dispatcher, with the parts of the real one the route uses
    dispatcher = types.SimpleNamespace(store=Store(reader=reader))
    # go through them
    for name in ("_spectrumRefused", "_dataDocument", "_dataDeliver"):
        # and bind each one to the stand-in
        setattr(dispatcher, name, functools.partial(getattr(qed.ux.dispatcher, name), dispatcher))
    # the server, with the responses and documents the route makes, and the crews if any
    server = types.SimpleNamespace(
        name="qed.test.server",
        responses=pyre.http.responses,
        documents=pyre.http.documents,
        fleet=fleet,
        deferred=Deferred,
    )
    # match the url the way the dispatcher does
    match = qed.ux.dispatcher.regex.match(url)
    # it is the spectrum route
    assert match.lastgroup == "spectrum", url
    # resolve it
    return qed.ux.dispatcher.spectrum(
        dispatcher, server=server, request=types.SimpleNamespace(url=url), match=match
    )


# a view decides whether its dataset has a spectrum
limit = qed.libqed.nisar.slc.fftLimit
# the one of an RSLC does, bound by what the transform takes
assert Store(reader=rslc).view(viewport=0).spectrumLimit() == limit
# the one of any other product does not
assert Store(reader=gslc).view(viewport=0).spectrumLimit() is None
# and neither does a view with nothing on display
empty = types.SimpleNamespace(reader=rslc, dataset=None)
assert qed.ux.view.spectrumLimit(empty) is None

# a region inside the raster
good = "/spectrum/0/route_rslc.L.A.HH/100x200+64x48"

# the client asked about a viewport that is not there
assert ask(url="/spectrum/3/route_rslc.L.A.HH/100x200+64x48", fleet=Fleet()).code == 404
# about a product that is not an RSLC
assert ask(url=good, reader=gslc, fleet=Fleet()).code == 404
# about a region that hangs over the edge of the raster
assert ask(url="/spectrum/0/route_rslc.L.A.HH/990x200+64x48", fleet=Fleet()).code == 404
# about a region longer than the transform takes
assert ask(url="/spectrum/0/route_rslc.L.A.HH/0x0+4096x8", fleet=Fleet()).code == 404
# with a window of decibels that is not a number
assert ask(url=good + "?range=loud", fleet=Fleet()).code == 404
# with a taper that is not known
assert ask(url=good + "?taper=kaiser", fleet=Fleet()).code == 404
# and to a server with no crews
assert ask(url=good, fleet=None).code == 404

# a request about a dataset the view no longer shows came too late
assert ask(url="/spectrum/0/route_rslc.L.B.HH/100x200+64x48", fleet=Fleet()).code == 410

# a request for new work
fleet = Fleet()
response = ask(url=good + "?range=40", fleet=fleet)
# is parked
assert isinstance(response, Deferred), response
# and can be withdrawn if the client hangs up
assert response.abandoned is not None
# while the crews get exactly one task
(task,) = fleet.rendered
# for the region and the window of decibels the client asked for, untapered
assert (task.origin, task.shape, task.range, task.taper) == ((100, 200), (64, 48), 40.0, False)

# a request for a tapered region
fleet = Fleet()
ask(url=good + "?taper=hann", fleet=fleet)
# hands the crews a task that tapers
(tapered,) = fleet.rendered
assert tapered.taper is True

# the same request, once its picture is on hand
fleet = Fleet()
fleet.cache[task] = qed.nexus.spool.stash(data=memoryview(b"a picture"))
response = ask(url=good + "?range=40", fleet=fleet)
# is served on the spot
assert response.code == 200, response.code
# and the crews are not bothered
assert fleet.rendered == []

# and a request whose work took a crew member down before
fleet = Fleet()
fleet.suspects.add(task)
# is refused before it reaches the crews
assert ask(url=good + "?range=40", fleet=fleet).code == 404
assert fleet.rendered == []


# end of file
