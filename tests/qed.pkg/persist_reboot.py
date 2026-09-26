#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a session starts where the previous one left off: booting out of the workspace
the persistence driver wrote finds the archive connected with its folder on display, the
folder listed again on first contact, and the view bound to its reader
"""

# externals
import os

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the workspace the persistence driver wrote
workspace = os.path.join(here, "persist_ws")
# if it is not there
if not os.path.exists(os.path.join(workspace, "qed.yaml")):
    # there is nothing to check
    raise SystemExit(0)
# work out of it
os.chdir(workspace)

# support
import qed

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store
# the archive is connected
archive = store.archive(uri=f"file:{here}")
assert archive is not None
# with its root on display
uri = str(archive.uri)
assert archive.expanded == [uri]
# but not listed yet, since boot touches nothing
assert archive.listing(uri=uri) is None
# first contact lists it
store.stage()
assert archive.listing(uri=uri) is not None
# and this driver is among the entries
assert "persist_reboot.py" in {item["name"] for item in archive.items()}
# the reader is connected
assert store.source(name="d16") is not None
# and the view is bound to it
views = [viewport.view() for viewport in store.viewports]
assert len(views) == 1
assert views[0].reader.pyre_name == "d16"


# end of file
