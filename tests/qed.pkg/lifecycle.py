#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the staging lifecycle: a source hands its product to a crew and the request returns
at once, the discovery record settles the standing when it arrives, a survey that fails
retains its reason, and a metadata-only twin can still be read on the spot

The crew is stood in for here, so the test stays a single process: a fleet that records
what it was asked to stage lets the driver deliver the outcome by hand, exactly the way a
team delivers it when a worker reports back
"""

# externals
import pickle

# support
import journal
import pyre
import qed

# the NISAR fixture this driver reads; part of the shared test data tree
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gslc.h5"
# if it has not been generated
if not product.exists():
    # there is nothing to check
    raise SystemExit(0)


# a stand-in for the fleet that parks staging requests instead of forking crews
class Fleet:
    """
    A fleet that remembers what it was asked to stage
    """

    # interface
    def stage(self, reader, callback):
        """
        Record the staging request so the driver can deliver its outcome by hand
        """
        # park the request
        self.requests.append((reader, callback))
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the staging requests i have received
        self.requests = []
        # all done
        return


# a change broadcaster that counts its calls, standing in for the event stream
class Notifier:
    """
    A broadcaster that remembers how many times it was rung
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # nobody has been told anything yet
        self.count = 0
        # all done
        return

    def __call__(self):
        # count the announcement
        self.count += 1
        # all done
        return


# get the configuration store
ns = pyre.executive.nameserver
# the priority factories
pri = pyre.executive.priority
# and a locator
loc = pyre.tracking.simple("while setting up the lifecycle test")

# configure the NISAR source; the deposit carries {command} priority so it beats the
# fixture configuration this test directory holds for the native suite
ns.insert(
    name="t.datasets",
    priority=pri.command(),
    locator=loc,
    value=("import:qed.readers.nisar.gslc#gslc",),
)
# point it at the product
ns.insert(name="gslc.uri", value=str(product), priority=pri.user(), locator=loc)

# quiet the configuration chatter
journal.warning("qed.cli").deactivate()
# and the staging complaints, since this driver stages a failure deliberately
journal.warning("qed.ux.staging").deactivate()

# boot the application
app = qed.shells.qed(name="t")
# and build its dispatcher explicitly, the way the test environment must
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the store
store = ux.store
# attach the stand-ins, the way the server wires the real fleet and event stream
fleet = Fleet()
notifier = Notifier()
store.fleet = fleet
store.notifier = notifier

# before anybody asks, the source is merely connected
assert store.lifecycle(name="gslc").status == "connected"

# stage the catalog
store.stage()
# the request went to the crew rather than opening anything here
assert len(fleet.requests) == 1
# the source is marked as under way
assert store.lifecycle(name="gslc").status == "staging"
# and nothing has been discovered, since no worker has reported yet
assert store.source(name="gslc").datasets == []
# the clients were told the standing moved
assert notifier.count == 1

# a second request while the survey is in flight is absorbed rather than duplicated
store.stage()
assert len(fleet.requests) == 1

# now produce the report a worker would have sent back, by surveying in this process
reader, callback = fleet.requests[0]
task = pickle.loads(pickle.dumps(qed.nexus.survey(reader=reader)))
record = pickle.loads(pickle.dumps(task.execute(readers={})))
# and deliver it the way a team delivers a completed task
callback(result=record, error=None)

# the source is now viewable
assert store.lifecycle(name="gslc").status == "ready"
# with no error to report
assert store.lifecycle(name="gslc").error is None
# the survey was timed
assert store.lifecycle(name="gslc").elapsed is not None
# its datasets reached the index, so the client can select one
assert store.dataset(name="gslc.L.A.HH") is not None
# and the clients were told again, so they refetch and see the discovery
assert notifier.count == 2

# the hydrated twins hold no payload
twin = store.dataset(name="gslc.L.A.HH")
assert twin.data is None
# but a peek can still read the product: the store opens a live copy on the spot, which is
# the escape hatch that keeps the profile and the pixel peek working
assert store.realize(dataset=twin).data is not None

# a second source, this time one whose survey fails
store.connectSource(
    source=qed.readers.nisar.gslc(name="doomed", uri="file:/nope/missing.h5")
)
# stage it alone
store.stage(name="doomed")
# it went to the crew
assert len(fleet.requests) == 2
# deliver the failure the way a team reports a casualty
reader, callback = fleet.requests[1]
callback(
    result=None, error=qed.nexus.exceptions.RecoverableError(description="no file")
)

# the source is marked as failed
assert store.lifecycle(name="doomed").status == "failed"
# retaining the reason, which is what the client displays
assert "no file" in store.lifecycle(name="doomed").error
# and it stays listed, so the user can see it and ask for a retry
assert store.source(name="doomed") is not None


# end of file
