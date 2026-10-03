#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a spectrum task survives a wire round trip and computes, on a worker, the same picture
the kernel does in place; equal requests are the same work, and a region past the limit is a
task failure that leaves the worker healthy
"""

# externals
import os
import pickle
import types

# support
import journal
import pyre
import qed

# the NISAR fixture; part of the shared test data tree
product = os.path.join(os.path.dirname(__file__), "..", "data", "nisar", "gslc.h5")
# if it has not been generated
if not os.path.exists(product):
    # there is nothing to check
    raise SystemExit(0)

# a reader over it
reader = qed.readers.nisar.gslc(name="spectrum_gslc", uri=product)
# make first contact
reader.open()
# and grab a dataset of complex samples
dataset, *_ = reader.datasets
# a stand-in for the view state behind a spectrum request
view = types.SimpleNamespace(reader=reader, dataset=dataset)

# a region inside the raster, with uneven sides
origin = (0, 0)
shape = tuple(min(extent, size) for extent, size in zip(dataset.shape, (64, 48)))

# the picture the kernel makes in place
data, _, _ = dataset.resolve(zoom=(0, 0))
reference = bytes(
    memoryview(
        qed.libqed.nisar.slc.fft(
            source=data, datatype=dataset.datatype.htype, origin=origin, shape=shape, range=60
        )
    )
)

# describe the request as a task
task = qed.nexus.spectrum(view=view, origin=origin, shape=shape)
# push it through the wire, the way the team marshals it to a crew member
task = pickle.loads(pickle.dumps(task))
# execute it the way a worker does: with a fresh reader registry, so the data source is
# rebuilt from the recipe the task carries
spool = task.execute(readers={})
# the picture is parked in a spool of the right size
assert spool.size == len(reference), (spool.size, len(reference))
# read the payload back
spool.file.seek(0)
picture = spool.file.read()
# and release the spool
spool.close()
# the worker made the same picture
assert picture == reference

# a request for the same region is the same work
assert task == qed.nexus.spectrum(view=view, origin=origin, shape=shape)
# but one over a different window of decibels is not
assert task != qed.nexus.spectrum(view=view, origin=origin, shape=shape, range=40)
# and neither is one over a different region
assert task != qed.nexus.spectrum(view=view, origin=(1, 0), shape=shape)

# a region longer than the limit is refused by the kernel; keep its report out of the output
journal.error("qed.nisar.slc.fft").device = journal.trash()
# ask for one
toolong = qed.nexus.spectrum(view=view, origin=origin, shape=(4096, 8))
# carefully
try:
    # execute it
    toolong.execute(readers={})
# the failure is one the crew member survives
except pyre.nexus.exceptions.RecoverableError:
    # as expected
    pass
# anything else
else:
    # is a failure of the check
    assert False, "a region past the limit was transformed"


# end of file
