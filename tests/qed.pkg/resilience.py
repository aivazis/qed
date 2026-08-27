#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the application boots despite misconfigured datasets: the store resolves the
configured entries one at a time, discarding the bad ones with a warning, and takes
ownership of the survivors
"""

# support
import journal
import pyre
import qed

# the c16 fixture that ships with the test suite
fixture = pyre.primitives.path(__file__).parent / "c16.dat"

# get the configuration store
ns = pyre.executive.nameserver
# the priority of a user configuration file
pri = pyre.executive.priority
# and a locator
loc = pyre.tracking.simple("while staging the resilience test")

# configure a pile with one good entry, one unresolvable family, and one reader whose
# construction fails with a raw {FileNotFoundError}; the latter two must not kill the boot;
# the deposit carries {command} priority so it beats the fixture configuration this test
# directory holds for the nexus suite
ns.insert(
    name="t.datasets",
    priority=pri.command(),
    locator=loc,
    value=(
        "import:qed.readers.native.flat#good",
        "import:qed.readers.nosuch#bogus",
        "import:qed.readers.isce2.slc#broken",
    ),
)
# point the good reader at the fixture, a 65x65 c16 raster
ns.insert(name="good.uri", value=str(fixture), priority=pri.user(), locator=loc)
ns.insert(name="good.cell", value="c16", priority=pri.user(), locator=loc)
ns.insert(name="good.shape", value="65,65", priority=pri.user(), locator=loc)
# and the broken one at a file that does not exist
ns.insert(name="broken.uri", value="/nope/missing.slc", priority=pri.user(), locator=loc)

# the discards are reported on this channel; quiet it so the test passes silently
journal.warning("qed.cli").deactivate()

# boot the application
app = qed.shells.qed(name="t")
# and build its dispatcher explicitly, the way the test environment must since it has no
# document root; constructing the store here used to die with an unhandled {FileNotFoundError}
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)

# the store survived
store = ux.store
# construction is passive, so only the unresolvable family was discarded at the handoff;
# the reader with the missing file constructs fine and survives until first contact
assert [source.pyre_name for source in store.sources] == ["good", "broken"]
# and no dataset exists yet, since nothing has touched a file
assert store.dataset(name="good.data") is None
# the plexus pile was emptied by the handoff
assert app.datasets == []

# initiate first contact, the way the server does when it is ready to serve
store.open()
# the reader with the missing file was discarded
assert [source.pyre_name for source in store.sources] == ["good"]
# and the survivor discovered its dataset
assert store.dataset(name="good.data") is not None


# end of file
