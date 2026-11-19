#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the store keeps the tree of a data archive: expanding a folder lists it and puts
its entries on display, each with the folder that holds it; refreshing lists every folder
on display again; collapsing a folder takes it and everything beneath it off display; and a
folder that cannot be listed records the reason without taking the archive down

Without a fleet the listings run in this process, which is what this driver exercises
"""

# externals
import os

# support
import journal
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store
# the store writes the archives back to the workspace file on every change; point the
# workspace at a scratch directory so the fixtures of this directory stay untouched
scratch = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_ws")
# make it
os.makedirs(scratch, exist_ok=True)
# and point the workspace at it
app.workspace.path = scratch
# no fleet is attached, so listings run here
assert store.fleet is None
# count the announcements
announcements = []
# by recording each one the store makes
store.notifier = lambda: announcements.append(1)

# the archive is the test tree, one level up
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# connect it
archive = qed.archives.local(name="browse_local", uri=f"file:{root}")
# and hand it to the store
store.connectArchive(archive=archive)
# its uri is how the mutations address it
uri = str(archive.uri)
# nothing is on display
assert archive.expanded == []
# so it shows no items
assert list(archive.items()) == []
# and its root is not expanded
assert not archive.isExpanded(uri=uri)

# expand the root
assert store.expandFolder(archive=uri, uri=uri) is archive
# the root is on display and its listing has landed
assert archive.isExpanded(uri=uri)
# it is not waiting for a listing
assert not archive.isPending(uri=uri)
# nothing went wrong
assert archive.failure(uri=uri) is None
# and the listing is on hand
assert archive.listing(uri=uri) is not None
# the clients were told
assert announcements
# the entries of the root are on display
items = list(archive.items())
# among them this directory
folders = {item["name"]: item for item in items if item["isFolder"]}
# pick it out
here = folders["qed.pkg"]
# held by the root
assert here["parent"] == uri
# not yet expanded
assert not here["expanded"]
# not waiting for a listing
assert not here["pending"]
# and with nothing wrong
assert here["error"] is None

# expand this directory
store.expandFolder(archive=uri, uri=here["uri"])
# the root and this directory are on display, in that order
assert archive.expanded == [uri, here["uri"]]
# the entries of both are on display
items = list(archive.items())
# this driver is among them, held by this directory
files = {item["name"]: item for item in items if item["parent"] == here["uri"]}
# is there
assert "browse.py" in files
# as a file
assert not files["browse.py"]["isFolder"]
# and this directory shows as expanded in the root's listing
assert {item["name"]: item for item in items if item["isFolder"]}["qed.pkg"]["expanded"]

# refresh
store.refreshArchive(uri=uri)
# both folders are still on display, listed anew
assert archive.expanded == [uri, here["uri"]]
# neither waiting for a listing
assert not archive.isPending(uri=uri)
# both of them
assert not archive.isPending(uri=here["uri"])
# and this driver is still among the entries of this directory
assert "browse.py" in {item["name"] for item in archive.items() if item["parent"] == here["uri"]}

# a folder that does not exist fails without taking the archive down
missing = f"file:{root}/no-such-folder"
# the failure is reported on a warning channel; this driver expects it
journal.warning("qed.ux.archives").deactivate()
# expand it
store.expandFolder(archive=uri, uri=missing)
# it is on display, its listing is over, and the reason is on record
assert archive.isExpanded(uri=missing)
# not waiting
assert not archive.isPending(uri=missing)
# with a failure on record
assert archive.failure(uri=missing) is not None
# and no listing
assert archive.listing(uri=missing) is None
# and the rest of the tree is intact
assert "browse.py" in {item["name"] for item in archive.items() if item["parent"] == here["uri"]}

# collapse this directory
store.collapseFolder(archive=uri, uri=here["uri"])
# it is off display, its listing forgotten, and the root still lists it as collapsed
assert archive.expanded == [uri, missing]
# so its listing is gone
assert archive.listing(uri=here["uri"]) is None
# and the root lists it as collapsed
assert not {item["name"]: item for item in archive.items() if item["isFolder"]}["qed.pkg"][
    "expanded"
]

# collapse the root
store.collapseFolder(archive=uri, uri=uri)
# everything is off display
assert archive.expanded == [missing]
# so there are no items
assert list(archive.items()) == []

# an unknown archive is reported, not raised
assert store.expandFolder(archive="file:/nowhere", uri="file:/nowhere") is None


# end of file
