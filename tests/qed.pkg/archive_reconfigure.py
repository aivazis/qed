#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that an archive the user reconfigures keeps its name and moves: the catalog finds it at
its new location and not at the old one, it forgets what it had on display, and it needs saving;
an archive cannot move to a location another one holds, or take a setting that is not one of its
traits, and either attempt leaves it where it was; an archive in a bucket builds a new session
for its new settings

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "archive_reconfigure_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it, with a few folders to turn into archives
os.makedirs(os.path.join(workspace, "one", "inner"))
os.makedirs(os.path.join(workspace, "two"))
os.makedirs(os.path.join(workspace, "three"))
# their locations
one = f"file:{os.path.realpath(os.path.join(workspace, 'one'))}"
two = f"file:{os.path.realpath(os.path.join(workspace, 'two'))}"
three = f"file:{os.path.realpath(os.path.join(workspace, 'three'))}"

# the configuration file
original = (
    "# -*- pyre -*-\n\n"
    "# the installation under test has no web client; keep the complaint about it quiet\n"
    "qed.journal.warning.qed.startup.assets:\n"
    "    active: no\n\n"
    "# end of file\n"
)
# write it
with open(os.path.join(workspace, "qed.yaml"), mode="w", encoding="utf-8") as stream:
    # all at once
    stream.write(original)

# work out of the scratch workspace, so its configuration file is the one that loads
os.chdir(workspace)

# support
import journal
import pyre
import qed

# the complaints about the moves this driver refuses are expected
journal.warning("qed.ux.archives").deactivate()

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store

# an archive at the wrong location
archive = store.connectArchive(archive=qed.archives.local(name="local:moving", uri=one))
# with a folder on display
store.expandFolder(archive=one, uri=one)
store.expandFolder(archive=one, uri=f"{one}/inner")
# saved, so the files know about it
store.persistArchive(uri=one)
# and so it has nothing new to say
assert not archive.dirty

# point it at the right location
moved = store.reconfigureArchive(uri=one, location=two, settings={})
# is the same archive
assert moved is archive
# with the same name
assert archive.pyre_name == "local:moving", archive.pyre_name
# at the new location
assert str(archive.uri) == two, archive.uri
# where the catalog finds it
assert store.archive(uri=two) is archive
# and not at the old one
assert store.archive(uri=one) is None
# it has nothing on display, since the folders it had belong to the old location
assert archive.expanded == [], archive.expanded
# and no listings
assert archive.listing(uri=one) is None
# and the files describe the old location, so it needs saving
assert archive.dirty
# until it is saved
store.persistArchive(uri=two)
# after which it has nothing new to say
assert not archive.dirty
# and the configuration file names the new location
with open("qed.yaml", mode="r", encoding="utf-8") as stream:
    # all at once
    text = stream.read()
# instead of the old one
assert two.removeprefix("file:") in text and one.removeprefix("file:") not in text, text
# and its listing works at the new location
store.expandFolder(archive=two, uri=two)
# which is empty
assert archive.listing(uri=two) is not None

# another archive
other = store.connectArchive(archive=qed.archives.local(name="local:other", uri=three))
# holds a location
assert store.archive(uri=three) is other
# that the first one cannot move to
assert store.reconfigureArchive(uri=two, location=three, settings={}) is None
# so it stays where it was
assert store.archive(uri=two) is archive and str(archive.uri) == two
# and so does the other one
assert store.archive(uri=three) is other and str(other.uri) == three

# a setting that is not a trait of the archive
try:
    # is refused
    store.reconfigureArchive(uri=two, location=one, settings={"bogus": "value"})
    # so we can't get here
    assert False, "unreachable"
# by the archive, which names it
except pyre.components.exceptions.TraitNotFoundError as error:
    # which names it
    assert error.name == "bogus", error.name
# and it stays where it was
assert store.archive(uri=two) is archive and str(archive.uri) == two

# an archive in a bucket
bucket = store.connectArchive(
    archive=qed.archives.s3(name="s3:moving", uri="s3://misspelled/products", region="us-west-2")
)
# that has built a session, stood in for here, since a real one goes looking for keys
bucket._session = object()
# pointed at the right bucket, with a profile and without a region
store.reconfigureArchive(
    uri="s3://misspelled/products",
    location="s3://spelled/products",
    settings={"profile": "science", "region": None},
)
# moves
assert store.archive(uri="s3://spelled/products") is bucket
# takes the new settings
assert bucket.profile == "science" and bucket.region is None, (bucket.profile, bucket.region)
# and lets go of its session, so the next request builds one for the new settings
assert bucket._session is None


# end of file
