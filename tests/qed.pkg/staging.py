#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the {stage} mutation initiates first contact with the connected sources and
that {Reader.status} reports the lifecycle honestly

The server boots its sources passively; the {stage} mutation is the client's declaration
that the catalog is relevant, so it must perform first contact, populate the catalog, and
flip the reported status from {connected} to {ready}. Staging is idempotent, and a
staging request may confine itself to a single named source
"""

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
loc = pyre.tracking.simple("while setting up the staging test")

# configure a single source; the deposit carries {command} priority so it beats the
# fixture configuration this test directory holds for the nexus suite
ns.insert(
    name="t.datasets",
    priority=pri.command(),
    locator=loc,
    value=("import:qed.readers.nisar.gslc#solo",),
)
# point it at the product
ns.insert(name="solo.uri", value=str(product), priority=pri.user(), locator=loc)

# quiet the configuration chatter
journal.warning("qed.cli").deactivate()

# boot the application
app = qed.shells.qed(name="t")
# and build its dispatcher explicitly, the way the test environment must
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the store
store = ux.store

# the query that reads the catalog status
catalog = "query { qed { readers { name status } } }"
# the staging mutation
stage = """
    mutation stage($payload: StageInput!) {
        stage(input: $payload) {
            readers { name status }
        }
    }
"""
# and the execution context the handlers build for every request
context = {"store": store}

# before staging, the catalog must report the source as merely connected
result = qed.gql.schema.execute(catalog, context=context)
# so the query succeeds
assert result.errors is None
# it finds the single passive source
readers = result.data["qed"]["readers"]
assert len(readers) == 1
assert readers[0]["name"] == "solo"
# the source has made no contact
assert readers[0]["status"] == "connected"
# and has discovered nothing
assert list(store.source(name="solo").datasets) == []

# stage the whole catalog
result = qed.gql.schema.execute(stage, context=context, variables={"payload": {}})
# the mutation succeeds
assert result.errors is None
# it reports the source as ready
readers = result.data["stage"]["readers"]
assert len(readers) == 1
assert readers[0]["status"] == "ready"
# and the source has discovered its datasets
assert len(store.source(name="solo").datasets) > 0

# staging again, confined to the named source, is a harmless no-op
result = qed.gql.schema.execute(
    stage, context=context, variables={"payload": {"reader": "solo"}}
)
# it succeeds
assert result.errors is None
# and still reports readiness
assert result.data["stage"]["readers"][0]["status"] == "ready"

# staging an unknown source draws a warning, not an error; keep the output quiet
journal.warning("qed.ux.staging").deactivate()
# fire the mutation at a phantom
result = qed.gql.schema.execute(
    stage, context=context, variables={"payload": {"reader": "phantom"}}
)
# it still resolves cleanly
assert result.errors is None


# end of file
