#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the store writes its state back into the workspace configuration file: a
connected archive gets a section and an entry in the archives list, its expansion follows,
the reader that came from the file keeps its section as written and is named in the datasets
list, and the views are written under session names

The driver works out of a scratch workspace with its own configuration file, so the fixtures
of this directory stay untouched; the reboot driver reads what this one writes
"""

# externals
import os
import shutil

# this directory
here = os.path.dirname(os.path.abspath(__file__))
# the scratch workspace
workspace = os.path.join(here, "persist_ws")
# a defensive guard against a stale one
if os.path.exists(workspace):
    # start clean
    shutil.rmtree(workspace)
# make it
os.makedirs(workspace)
# with a configuration file that points at the raster in this directory
with open(os.path.join(workspace, "qed.yaml"), mode="w", encoding="utf-8") as stream:
    # write it
    stream.write("""# -*- pyre -*-

# the location of the rasters
qed.native: ..

# the dataset, spelled with a macro that must survive
d16:
    uri: "{qed.native}/c16.dat"
    shape: 65, 65
    cell: c16

# connect it
datasets:
    - qed.readers.native.flat#d16

# end of file
""")
# work out of the scratch workspace, so its configuration file is the one that loads
os.chdir(workspace)

# support
import pyre
import qed

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the store
store = ux.store
# no fleet is attached, so listings run here
assert store.fleet is None

# connect an archive over this directory
archive = qed.archives.local(name="persist_local", uri=f"file:{here}")
store.connectArchive(archive=archive)
# its uri
uri = str(archive.uri)
# expand it
store.expandFolder(archive=uri, uri=uri)
# and write everything, views included
written = store.persist()
# the workspace file was written, and nothing else
assert [os.path.abspath(str(path)) for path in written] == [os.path.join(workspace, "qed.yaml")]

# read it back
doc = pyre.config.newYamlEditor(uri="qed.yaml")
# the archive has a section with what the session assigned
assert doc.get("persist_local", "uri") == f"file:{here}"
assert list(doc.get("persist_local", "expanded")) == [uri]
# the default workspace archive, which came from code with nothing assigned, has no section
assert doc.get("local:workspace") is None
# both are in the archives list
archives = list(doc.get("archives"))
assert "qed.archives.local#persist_local" in archives
assert "qed.archives.local#local:workspace" in archives
# the reader keeps its section exactly as written, macro and all
assert doc.get("d16", "uri") == "{qed.native}/c16.dat"
assert doc.get("d16", "shape") == "65, 65"
# and is named in the datasets list
assert list(doc.get("datasets")) == ["qed.readers.native.flat#d16"]
# the single view was written under a session name
assert list(doc.get("views")) == ["qed.ux.views.view#view.0"]
# bound to the reader
assert doc.get("view.0", "reader") == "qed.readers.native.flat#d16"

# a second write is idempotent
store.persist()
again = pyre.config.newYamlEditor(uri="qed.yaml")
assert again.render() == doc.render()


# end of file
