#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that archive credentials survive the trip to a worker: the reader retains them, the
recipe carries them, the rebuilt reader presents them, and the tile identity excludes them

The reader opens the NISAR fixture, whose local scheme ignores credentials, so the plumbing
is verifiable without an S3 archive; when the fixture has not been generated, there is
nothing to check and the driver exits quietly
"""

# externals
import os
import pickle
import types

# support
import qed

# the NISAR fixture this driver reads; part of the shared test data tree
product = os.path.join(os.path.dirname(__file__), "..", "data", "nisar", "gslc.h5")
# if it has not been generated
if not os.path.exists(product):
    # there is nothing to check
    raise SystemExit(0)

# the access credentials a stand-in archive grants
grant = {"region": "us-west-2", "access_key": "AKIATEST", "secret_key": "sekrit"}

# a stand-in for an archive
archive = types.SimpleNamespace(credentials=lambda: dict(grant))

# a managed reader pulls its credentials from its archive at first contact
managed = qed.readers.nisar.gslc(name="cred_managed", uri=product, archive=archive)
# construction is passive, so nothing has been granted yet
assert managed.credentials == {}
# make first contact
managed.open()
# and check that the grant was retained
assert managed.credentials == grant

# an unmanaged reader has none
plain = qed.readers.nisar.gslc(name="cred_plain", uri=product)
plain.open()
assert plain.credentials == {}

# describe a tile of the managed reader
dataset = managed.find(selector={"band": "L", "frequency": "A", "polarization": "HH"})
pipeline = dataset.channel(name="amplitude")
view = types.SimpleNamespace(reader=managed, dataset=dataset, pipeline=lambda channel: pipeline)
task = qed.nexus.tile(
    view=view, channel="cred.amplitude", zoom=(4, 4), origin=(0, 0), shape=(32, 32)
)
# the recipe carries the credentials
assert dict(task.config)["credentials"] == grant
# but the identity does not: a rotated token must not invalidate cached work
assert "sekrit" not in repr(task.identity)

# render the reference inline
reference = bytes(
    memoryview(dataset.render(channel=pipeline, zoom=(4, 4), origin=(0, 0), shape=(32, 32)))
)

# push the task through the wire and execute it the way a worker does; the rebuilt reader
# presents the credentials, which the local scheme ignores
task = pickle.loads(pickle.dumps(task))
spool = task.execute(readers={})
# read the payload back
spool.file.seek(0)
tile = spool.file.read()
spool.close()
# the worker render matches the inline reference
assert tile == reference


# end of file
