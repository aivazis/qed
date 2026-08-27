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

# configure a pile with one good entry, one unresolvable family, one reader whose
# construction fails with a raw {FileNotFoundError}, and one whose declared shape does not
# fit in its file; none of them may kill the boot; the deposit carries {command} priority
# so it beats the fixture configuration this test directory holds for the nexus suite
ns.insert(
    name="t.datasets",
    priority=pri.command(),
    locator=loc,
    value=(
        "import:qed.readers.native.flat#good",
        "import:qed.readers.nosuch#bogus",
        "import:qed.readers.isce2.slc#broken",
        "import:qed.readers.native.flat#short",
    ),
)
# point the good reader at the fixture, a 65x65 c16 raster
ns.insert(name="good.uri", value=str(fixture), priority=pri.user(), locator=loc)
ns.insert(name="good.cell", value="c16", priority=pri.user(), locator=loc)
ns.insert(name="good.shape", value="65,65", priority=pri.user(), locator=loc)
# point the broken one at a file that does not exist
ns.insert(
    name="broken.uri", value="/nope/missing.slc", priority=pri.user(), locator=loc
)
# and declare a shape one sample too large for the short one, which would otherwise let
# the render machinery read past the end of the map
ns.insert(name="short.uri", value=str(fixture), priority=pri.user(), locator=loc)
ns.insert(name="short.cell", value="c16", priority=pri.user(), locator=loc)
ns.insert(name="short.shape", value="65,66", priority=pri.user(), locator=loc)
# n.b.: a broken view entry rides the same per-entry containment as the datasets, but it
# cannot be exercised from this directory: resolving an unresolvable spec sends the pyre
# linker shelf-hunting, and it imports {views.py} -- a test driver with module level side
# effects -- so the scenario is left to the datasets entries above

# the discards are reported on these channels; quiet them so the test passes silently
journal.warning("qed.cli").deactivate()
journal.warning("qed.readers.native.flat").deactivate()

# boot the application
app = qed.shells.qed(name="t")
# and build its dispatcher explicitly, the way the test environment must since it has no
# document root; constructing the store here used to die with an unhandled {FileNotFoundError}
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)

# the store survived
store = ux.store
# construction is passive, so only the unresolvable family was discarded at the handoff;
# the readers with the missing file and the oversized shape construct fine and survive
# until first contact
assert [source.pyre_name for source in store.sources] == ["good", "broken", "short"]
# and no dataset exists yet, since nothing has touched a file
assert store.dataset(name="good.data") is None
# the plexus pile was emptied by the handoff
assert app.datasets == []
# with no view configuration, there is a single blank viewport
assert len(list(store.viewports)) == 1

# bind the doomed source to the viewport, the way persisted state might
store.selectSource(viewport=0, name="broken")
# and check that it took
assert store.view(viewport=0).reader is not None

# initiate first contact, the way the server does when it is ready to serve
store.open()
# the reader with the missing file was discarded; the one with the oversized shape was
# contained and stays connected, exposing no datasets
assert [source.pyre_name for source in store.sources] == ["good", "short"]
# the good survivor discovered its dataset
assert store.dataset(name="good.data") is not None
# the short one did not
assert store.dataset(name="short.data") is None
# and the viewport bound to the casualty was reset
assert store.view(viewport=0).reader is None


# end of file
