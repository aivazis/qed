#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that selecting a flat raster with a fleet attached leaves it unprepared: a memory
mapped dataset knows nothing of levels, so no preparation is opened and the view renders
straight off the product, instead of the selection failing on the companions only products
with levels have
"""

# support
import pyre
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store
# make first contact with the sources, the way the server does when it is ready
store.open()
# attach a fleet, so that preparation is on the table
fleet = qed.nexus.fleet(name="qed.test.fleet")
fleet.dispatcher = pyre.ipc.newPSL()
store.fleet = fleet

# select the flat raster in the first viewport
view = store.selectSource(viewport=0, name="d16")
# the view landed on its dataset
assert view.dataset is not None
assert view.dataset.pyre_name == "d16.data"
# and nothing was prepared, since a memory mapped raster has no levels
assert store.preparation(name="d16.data") is None

# send everybody home
fleet.disband()


# end of file
