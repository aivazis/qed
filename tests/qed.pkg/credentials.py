#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that archive credentials survive the trip to a worker: the reader gets them from its
archive whenever it is asked, the recipe carries them, the rebuilt reader presents them, and
the task identity excludes them

The grant must not depend on the reader having made first contact in the process that
describes the work: first contact is a survey, which happens on a worker, so the reader on
the team side never opens its product; a recipe that only carried what {open} had left behind
would send the worker to the archive empty handed

The second half opens the NISAR fixture, whose local scheme ignores credentials, so the
plumbing is verifiable without an S3 archive; when the fixture has not been generated, that
half has nothing to check and the driver exits quietly
"""

# externals
import os
import pickle
import types

# support
import qed

# the access credentials a stand-in archive grants
grant = {"region": "us-west-2", "access_key": "AKIATEST", "secret_key": "sekrit", "token": "one"}

# a stand-in for an archive; it hands out a copy of whatever the grant is when it is asked
archive = types.SimpleNamespace(credentials=lambda: dict(grant))

# a reader connected through an archive, to a product that only a worker will ever open
remote = qed.readers.nisar.gslc(
    name="cred_remote", uri="s3://bucket/products/gslc.h5", archive=archive
)
# describe its first contact, the way the server does: without opening anything
survey = qed.nexus.survey(reader=remote)
# the reader is still untouched
assert remote._opened is False
# and yet the recipe carries the grant, so the worker can get at the product
assert dict(survey.config)["credentials"] == grant
# but the identity does not: a rotated token must not make this look like different work
assert "sekrit" not in repr(survey.identity)

# when the archive rotates its token
grant["token"] = "two"
# the next description of the same work
again = qed.nexus.survey(reader=remote)
# carries the fresh grant, since the reader asks its archive every time
assert dict(again.config)["credentials"]["token"] == "two"
# while the earlier recipe is a snapshot and keeps what it was given
assert dict(survey.config)["credentials"]["token"] == "one"
# and the two are still the same work
assert again == survey

# a reader with no archive and no credentials of its own has nothing to ship
bare = qed.readers.nisar.gslc(name="cred_bare", uri="s3://bucket/products/gslc.h5")
# so its recipe carries none
assert "credentials" not in dict(qed.nexus.survey(reader=bare).config)

# a reader that was handed credentials directly, the way a worker rebuilds one from a recipe
rebuilt = qed.readers.nisar.gslc(
    name="cred_rebuilt", uri="s3://bucket/products/gslc.h5", credentials=dict(grant)
)
# presents exactly those
assert rebuilt.credentials == grant


# the NISAR fixture the rest of this driver reads; part of the shared test data tree
product = os.path.join(os.path.dirname(__file__), "..", "data", "nisar", "gslc.h5")
# if it has not been generated
if not os.path.exists(product):
    # there is nothing further to check
    raise SystemExit(0)

# a managed reader of a product that can be opened here
managed = qed.readers.nisar.gslc(name="cred_managed", uri=product, archive=archive)
# make first contact
managed.open()
# the grant is the same before and after: it comes from the archive, not from having opened
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
