#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a memory-mapped dataset refuses a file smaller than its declared shape

A mapping is laid over the file without looking, and a read past the end of a file that is
shorter than the shape it was declared with is a crash rather than an error. The dataset
measures the file before mapping it and refuses, with a complaint that says by how much
"""

# support
import journal
import pyre
import qed

# the fixture: 65x65 complex pairs of shorts
fixture = pyre.primitives.path(__file__).parent / "c16.dat"

# the complaint is an error, and errors are fatal
channel = journal.error("qed.readers.native")
# keep it quiet
channel.device = journal.trash()

# a dataset that declares one row too many
try:
    # is refused when it opens
    qed.readers.native.datasets.mmap(
        name="short", uri=f"file:{fixture}", cell="c16", shape=(66, 65)
    )
# by the error
except journal.ApplicationError:
    # which is the point
    pass
# anything else is a failure
else:
    # so say so
    raise AssertionError("a short file was mapped")

# a dataset whose file is missing altogether is refused the same way
try:
    # by the error
    qed.readers.native.datasets.mmap(
        name="missing", uri="file:/no/such/file.dat", cell="c16", shape=(65, 65)
    )
# which is the point
except journal.ApplicationError:
    # so move on
    pass
# anything else is a failure
else:
    # so say so
    raise AssertionError("a missing file was mapped")

# a dataset that declares exactly what the file holds maps it
dataset = qed.readers.native.datasets.mmap(
    name="whole", uri=f"file:{fixture}", cell="c16", shape=(65, 65)
)
# and has a payload
assert dataset.data is not None
# with the declared shape
assert tuple(dataset.shape) == (65, 65)

# end of file
