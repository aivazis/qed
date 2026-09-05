#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a survey task survives a wire round trip and that hydrating a passive reader
from its discovery record reproduces what first contact would have found

The survey is the only first contact in the redesigned staging path: a crew member rebuilds
the reader from its recipe, opens the product, and ships back a record of plain values. The
team side reader hydrates from that record, materializing metadata-only dataset twins whose
channels tune themselves from the seed the worker measured, so nothing in the server process
ever touches the file
"""

# externals
import pickle

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the passive reader, before anybody has touched its file
reader, *_ = ux.store.sources
# describe its product as a survey task
task = qed.nexus.survey(reader=reader)
# push it through the wire, the way the team marshals it to a crew member
task = pickle.loads(pickle.dumps(task))
# execute it the way a worker does: with a fresh reader registry, so the data source is
# rebuilt from the recipe the task carries and opened in this process
record = pickle.loads(pickle.dumps(task.execute(readers={})))

# the record knows what the worker found
assert len(record.findings) > 0
# and the reader it surveyed is still untouched on this side
assert reader.datasets == []

# hydrate the passive reader from the record
record.hydrate(reader=reader)
# it now reports first contact
assert reader._opened is True
# with a twin for every dataset the worker found
assert len(reader.datasets) == len(record.findings)

# build a reference by opening the product the blocking way, in a second reader built from
# the same recipe the survey traveled with
factory = qed.protocols.reader.pyre_resolveSpecification(spec=task.factory)
reference = factory(name="reference", **task.config)
# make first contact
reference.open()

# the twins carry the same identities as the live datasets
assert [dict(data.selector) for data in reader.datasets] == [
    dict(data.selector) for data in reference.datasets
]
# the same layout
assert [tuple(data.shape) for data in reader.datasets] == [
    tuple(data.shape) for data in reference.datasets
]
assert [tuple(data.tile) for data in reader.datasets] == [
    tuple(data.tile) for data in reference.datasets
]
# and the same channels
assert [sorted(data.channels) for data in reader.datasets] == [
    sorted(data.channels) for data in reference.datasets
]

# the availability map and the auto-picked selections crossed intact
assert reader.available == reference.available
assert dict(reader.selections) == dict(reference.selections)

# the seed statistics crossed the wire unchanged, so the twins carry exactly what the
# surveying worker measured; tuning the channels from that seed is what {hydration} checks
assert [data.stats for data in reader.datasets] == [data.stats for data in reference.datasets]

# the twins are named the way the live datasets are, so the configuration this directory
# holds for the {d16} pipelines reaches them; the fixture pins every controller, which is
# what a user who has adjusted the display gets, and those pins must survive hydration
twin, *_ = reader.datasets
# get the pinned amplitude controller
amplitude = twin.channel(name="amplitude").amplitude
# the user's pin is in force
assert amplitude.auto is False
# with the bounds the configuration asked for, rather than anything derived from the seed
assert amplitude.low == -0.5
assert amplitude.high == 0.5

# a twin holds no payload, so nothing in this process opened the file
assert all(data.data is None for data in reader.datasets)


# end of file
