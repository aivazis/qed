#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a view built before its reader established first contact adopts the reader's
auto-picked selections when the store opens its sources

The boot path constructs views passively: a single source is auto-selected into the blank
viewport while its reader has empty selections, and first contact later auto-picks the
single-valued selector axes on the reader. The view must adopt those picks during the
refresh, because the client deliberately makes single-valued axes inert, so a view that
misses them can never complete its selection interactively
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
loc = pyre.tracking.simple("while staging the selection test")

# configure a single source, so the boot path auto-selects it into the blank viewport;
# the deposit carries {command} priority so it beats the fixture configuration this test
# directory holds for the nexus suite
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

# the single source was auto-selected into the viewport while still passive
view = store.view(viewport=0)
# so it is bound to the reader
assert view.reader is not None
# with no selections, since the reader has not made first contact
assert dict(view.selections) == {}

# initiate first contact, the way the server does when it is ready to serve
store.open()

# the reader auto-picked its single-valued axes during first contact
reader = store.source(name="solo")
# the fixture must realize at least one single-valued axis for this check to have teeth
assert len(reader.selections) > 0
# and the view adopted the picks during its refresh
view = store.view(viewport=0)
assert dict(view.selections) == dict(reader.selections)


# end of file
