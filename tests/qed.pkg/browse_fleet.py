#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a listing travels to a worker: with a fleet attached, expanding a folder hands the
listing to the scouts of the archive, the mutation returns with the folder pending, and the
manifest lands through the callback and moves the tree
"""

# externals
import os

# support
import pyre
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the store
store = ux.store
# build a fleet
fleet = qed.nexus.fleet(name="qed.test.fleet")
# give it an event loop
fleet.dispatcher = pyre.ipc.newPSL()
# and attach it to the store
store.fleet = fleet

# the archive is the test tree, one level up
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# connect it
archive = qed.archives.local(name="browse_worker", uri=f"file:{root}")
store.connectArchive(archive=archive)
# its uri is how the mutations address it
uri = str(archive.uri)


# the announcement handler winds down the loop once nothing is pending
def notifier():
    """
    Stop the event loop when the listing has landed
    """
    # if the listing is over
    if not archive.isPending(uri=uri):
        # stop the loop
        fleet.dispatcher.stop()
    # all done
    return


# attach it
store.notifier = notifier

# expand the root
store.expandFolder(archive=uri, uri=uri)
# the listing is under way on a worker
assert archive.isPending(uri=uri)
assert archive.listing(uri=uri) is None
# the scouts of this archive were formed
assert set(fleet.explorers) == {archive.pyre_name}
# with a single member
assert fleet.explorers[archive.pyre_name].size == 1
# spin the event loop until the manifest lands
fleet.dispatcher.watch()
# the listing is over
assert not archive.isPending(uri=uri)
assert archive.failure(uri=uri) is None
# and this directory is among the entries
items = {item["name"]: item for item in archive.items()}
assert items["qed.pkg"]["isFolder"]
assert items["qed.pkg"]["parent"] == uri

# disconnecting the archive sends its scouts home
store.disconnectArchive(uri=uri)
assert not fleet.explorers

# send everybody home
fleet.disband()


# end of file
