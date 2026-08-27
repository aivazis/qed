#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that aggregate tiles travel to workers: the stack recipe rebuilds the members, the
participation mask rides along, and the render matches the inline reference

The stack is assembled over the NISAR fixture; when it has not been generated, there is
nothing to check and the driver exits quietly
"""

# externals
import os
import pickle
import types

# support
import qed

# the NISAR fixture this driver stacks; part of the shared test data tree
product = os.path.join(os.path.dirname(__file__), "..", "data", "nisar", "gslc.h5")
# if it has not been generated
if not os.path.exists(product):
    # there is nothing to check
    raise SystemExit(0)

# build a two member stack over the same product
one = qed.readers.nisar.gslc(name="agg_one", uri=product)
two = qed.readers.nisar.gslc(name="agg_two", uri=product)
stack = qed.stacks.stack(name="agg", readers=[one, two])
# make first contact, which also opens the members
stack.open()
# find the aggregate dataset
dataset = stack.find(selector={"band": "L", "frequency": "A", "polarization": "HH"})
# grab its mean power pipeline
pipeline = dataset.channel(name="meanpower")
# and render the reference tile inline, over the full membership
reference = bytes(
    memoryview(
        dataset.render(
            channel=pipeline,
            zoom=(4, 4),
            origin=(0, 0),
            shape=(64, 64),
            mask=[True, True],
        )
    )
)

# assemble a stand-in for the view state behind an aggregate tile request
view = types.SimpleNamespace(
    reader=stack,
    dataset=dataset,
    pipeline=lambda channel: pipeline,
    members=[True, True],
)

# describe the tile as a task
task = qed.nexus.tile(
    view=view,
    channel="agg.L.A.HH.meanpower",
    zoom=(4, 4),
    origin=(0, 0),
    shape=(64, 64),
)
# the task knows it renders an aggregate
assert task.stacked
# over the full membership
assert task.mask == [True, True]
# and its recipe carries one entry per member
assert len(dict(task.config)["readers"]) == 2

# the participation mask is part of the identity
partial = qed.nexus.tile(
    view=types.SimpleNamespace(
        reader=stack,
        dataset=dataset,
        pipeline=lambda channel: pipeline,
        members=[True, False],
    ),
    channel="agg.L.A.HH.meanpower",
    zoom=(4, 4),
    origin=(0, 0),
    shape=(64, 64),
)
assert task != partial

# push the task through the wire, the way the team marshals it to a crew member
task = pickle.loads(pickle.dumps(task))
# execute it the way a worker does: a fresh registry, so the stack and both members are
# rebuilt from the recipe with their own file handles
spool = task.execute(readers={})
# read the payload back
spool.file.seek(0)
tile = spool.file.read()
spool.close()
# the worker render matches the inline reference
assert tile == reference


# end of file
