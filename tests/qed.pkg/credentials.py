#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check how a reader assembles what it presents to the infrastructure in order to open its
product, and that it survives the trip to a worker

The grant starts out empty; what the archive hands out goes in first, the reader's own
{credentials} go in last and win, and whatever is still missing is looked up by whoever opens
the product. The reader's {credentials} are what the user wrote, and nothing else: they never
absorb what the archive hands out, so saving a reader cannot write keys into a file

The grant must not depend on the reader having made first contact in the process that
describes the work: first contact is a survey, which happens on a worker, so the reader on
the team side never opens its product

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
from qed.readers import access

# what a stand-in archive hands out
keys = {"region": "us-west-2", "access_key": "AKIATEST", "secret_key": "sekrit", "token": "one"}
# a stand-in for an archive; it hands out a copy of whatever the keys are when it is asked
archive = types.SimpleNamespace(credentials=lambda: dict(keys))
# a product that only a worker will ever open
uri = "s3://bucket/products/gslc.h5"

# a reader connected through an archive
remote = qed.readers.nisar.gslc(name="cred_remote", uri=uri, archive=archive)
# its own credentials are what the user wrote, which is nothing
assert dict(remote.credentials) == {}
# while its grant is what the archive hands out
assert remote.grant(resolve=False) == keys
# describe its first contact, the way the server does: without opening anything
survey = qed.nexus.survey(reader=remote)
# the reader is still untouched
assert remote._opened is False
# and yet the recipe carries the grant, so the worker can get at the product
assert dict(survey.config)["credentials"] == keys
# but the identity does not: a rotated token must not make this look like different work
assert "sekrit" not in repr(survey.identity)
# none of which rubbed off on the reader: there is still nothing of its own to save
assert dict(remote.credentials) == {}

# when the archive rotates its token
keys["token"] = "two"
# the next description of the same work
again = qed.nexus.survey(reader=remote)
# carries the fresh grant, since the reader asks its archive every time
assert dict(again.config)["credentials"]["token"] == "two"
# while the earlier recipe is a snapshot and keeps what it was given
assert dict(survey.config)["credentials"]["token"] == "one"
# and the two are still the same work
assert again == survey

# a reader that the user wired by hand, with no archive in sight
wired = qed.readers.nisar.gslc(
    name="cred_wired", uri=uri, credentials={"profile": "st", "region": "eu-west-1"}
)
# presents what it was told, and leaves the lookup to whoever opens the product
assert wired.grant(resolve=False) == {"profile": "st", "region": "eu-west-1"}
# which is what travels
assert dict(qed.nexus.survey(reader=wired).config)["credentials"] == {
    "profile": "st",
    "region": "eu-west-1",
}

# a reader with an archive and settings of its own: its own win
both = qed.readers.nisar.gslc(
    name="cred_both", uri=uri, archive=archive, credentials={"region": "eu-west-1"}
)
merged = both.grant(resolve=False)
assert merged["region"] == "eu-west-1"
assert merged["access_key"] == "AKIATEST"

# a reader with no archive and no settings has nothing to ship
bare = qed.readers.nisar.gslc(name="cred_bare", uri=uri)
assert bare.grant(resolve=False) == {}
assert "credentials" not in dict(qed.nexus.survey(reader=bare).config)

# a reader rebuilt on a worker from a recipe presents exactly what the recipe carried
rebuilt = qed.readers.nisar.gslc(name="cred_rebuilt", uri=uri, credentials=dict(keys))
assert rebuilt.grant(resolve=False) == keys

# the lookup of what is missing; stand in for the AWS chain, and note what it is asked
asked = []


def chain(profile=None, region=None):
    # record the request
    asked.append((profile, region))
    # and find some keys, along with the region the profile names
    return {"access_key": "AKIACHAIN", "secret_key": "found", "region": "us-east-2"}


# install it
access.chain = chain

# a grant that carries its keys is left alone
assert access.resolve(uri=uri, grant=keys) == keys
assert asked == []
# one that names a profile has its keys looked up under it; the region it names wins over
# the one the chain found, and the token, which the chain did not find, is there but blank
found = access.resolve(uri=uri, grant={"profile": "st", "region": "eu-west-1"})
assert asked == [("st", "eu-west-1")]
assert found["access_key"] == "AKIACHAIN"
assert found["region"] == "eu-west-1"
assert found["token"] == ""
# an empty grant gets whatever the chain comes up with, which is what an instance that runs
# next to the data expects
found = access.resolve(uri=uri, grant={})
assert asked[-1] == (None, None)
assert (found["access_key"], found["region"]) == ("AKIACHAIN", "us-east-2")
# a chain that comes up empty leaves a grant with every field the driver expects, all blank
# but the region of last resort, which is how the driver is told that the bucket is public
access.chain = lambda profile=None, region=None: {}
assert access.resolve(uri=uri, grant={}) == {
    "region": "us-west-2",
    "access_key": "",
    "secret_key": "",
    "token": "",
}
# and a product that does not live in a bucket needs none of this
assert access.resolve(uri="file:/somewhere/gslc.h5", grant={}) == {}
# the full grant of the bare reader goes through the lookup
assert bare.grant()["region"] == "us-west-2"


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
# opening it changed nothing about what it would save
assert dict(managed.credentials) == {}
# and its grant is what the archive hands out, as before
assert managed.grant(resolve=False) == keys

# an unmanaged reader has none
plain = qed.readers.nisar.gslc(name="cred_plain", uri=product)
plain.open()
assert dict(plain.credentials) == {}

# describe a tile of the managed reader
dataset = managed.find(selector={"band": "L", "frequency": "A", "polarization": "HH"})
pipeline = dataset.channel(name="amplitude")
view = types.SimpleNamespace(reader=managed, dataset=dataset, pipeline=lambda channel: pipeline)
task = qed.nexus.tile(
    view=view, channel="cred.amplitude", zoom=(4, 4), origin=(0, 0), shape=(32, 32)
)
# the recipe carries the credentials
assert dict(task.config)["credentials"] == keys
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
