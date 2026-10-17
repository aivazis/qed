#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a tile whose selector matches no dataset of the reader its worker rebuilt fails as
a recoverable error that can be read

pyre reads the description of an error as a template, so a description that carries the
rendering of a table, braces and all, cannot be rendered, and the failure escapes the crew
member instead of being reported
"""

# externals
import os
import pickle
import types

# support
import qed

# the raster in this directory
raster = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c16.dat")
# a reader over it
reader = qed.readers.native.flat(name="mismatch", uri=raster, shape=(65, 65), cell="c16")
# make first contact
reader.open()
# get its dataset
dataset, *_ = reader.datasets
# and its amplitude pipeline
pipeline = dataset.channel(name="amplitude")

# assemble a stand-in for the view state behind a tile request
view = types.SimpleNamespace(reader=reader, dataset=dataset, pipeline=lambda channel: pipeline)
# describe the tile as a task
task = qed.nexus.tile(
    view=view, channel="mismatch.amplitude", zoom=(0, 0), origin=(0, 0), shape=(64, 64)
)
# push it through the wire, the way the team marshals it to a crew member
task = pickle.loads(pickle.dumps(task))

# go through selectors the rebuilt reader cannot match
for selector, spec in [
    ({"band": "2"}, "band=2"),
    ({"frequency": "A", "polarization": "HH"}, "frequency=A, polarization=HH"),
]:
    # point the task at a dataset the reader does not have
    task.selector = selector
    # execute it the way a worker does
    try:
        # with a fresh reader registry, so the reader is rebuilt from the recipe
        task.execute(readers={})
    # the failure must be one the crew member reports and survives
    except task.RecoverableError as error:
        # whose description can be rendered, and names the selector it could not match
        assert str(error) == f"no dataset matches the selector {spec}"
    # anything else
    else:
        # is a failure to complain
        assert False, "a tile with no dataset to render succeeded"


# end of file
