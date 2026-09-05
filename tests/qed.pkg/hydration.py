#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the channels of a hydrated dataset tune themselves from the survey seed exactly
as they would have on the blocking path

This is the property the redesign rests on: the first tile a user sees must be correctly
tuned, with no retuning moment in front of them. The check runs against the NISAR fixture,
whose product has a rich selector tree and, unlike the native fixture in this directory,
pins no controller configuration, so the autotune is what actually sets the bounds
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

# get the configuration store
ns = pyre.executive.nameserver
# the priority factories
pri = pyre.executive.priority
# and a locator
loc = pyre.tracking.simple("while setting up the hydration test")

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

# boot the application
app = qed.shells.qed(name="t")
# and build its dispatcher explicitly, the way the test environment must
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the passive reader, before anybody has touched its file
reader = ux.store.source(name="gslc")

# describe its product as a survey task, push it through the wire, and execute it the way
# a worker does: a fresh registry, so the reader is rebuilt from the recipe and opened
task = pickle.loads(pickle.dumps(qed.nexus.survey(reader=reader)))
record = pickle.loads(pickle.dumps(task.execute(readers={})))
# hydrate the passive reader from what came back
record.hydrate(reader=reader)

# build a reference by opening the product the blocking way, from the same recipe
factory = qed.protocols.reader.pyre_resolveSpecification(spec=task.factory)
reference = factory(name="reference", **task.config)
# make first contact
reference.open()

# the rich selector tree crossed intact
assert len(reader.datasets) == len(reference.datasets)
assert len(reader.datasets) > 1
assert reader.available == reference.available

# go through the twins and their live counterparts
for twin, live in zip(reader.datasets, reference.datasets):
    # they describe the same dataset
    assert dict(twin.selector) == dict(live.selector)
    # go through the channels of the twin
    for tag, pipeline in twin.channels.items():
        # find the live counterpart
        peer = live.channels[tag]
        # walk the controllers of both in step
        for (controller, _), (mirror, _) in zip(pipeline.controllers(), peer.controllers()):
            # nothing pins these, so both tuned themselves from the same statistics
            assert controller.auto == mirror.auto
            # and arrived at the same display bounds
            assert getattr(controller, "low", None) == getattr(mirror, "low", None)
            assert getattr(controller, "high", None) == getattr(mirror, "high", None)

# and the twins hold no payload, so nothing in this process touched the product
assert all(twin.data is None for twin in reader.datasets)


# end of file
