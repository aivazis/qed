#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a raster whose every cell holds the same value, e.g. one that is all zeros, tunes
its controllers to a range that can render, instead of dividing by zero or collapsing the
picks onto each other; this is issue #81
"""

# externals
import tempfile

# support
import journal
import pyre
import qed

# the probe reports the lack of spread on a channel that would otherwise break the silence
journal.warning("qed.readers.statistics").device = journal.trash()

# a constant sample, the shape the probe hands out
zeros = (0.0, 0.0, 0.0)

# a log range controller has nothing to learn from it
log = qed.controllers.logRange(name="constant_log")
# remember its configured values
configured = (log.min, log.low, log.high, log.max)
# tuning does not raise
log.autotune(stats=zeros)
# and leaves the configuration alone
assert (log.min, log.low, log.high, log.max) == configured
# a sample with a zero floor but a positive ceiling is fine: the floor gets clipped
log.autotune(stats=(0.0, 0.5, 2.0))
assert log.min < log.low < log.high < log.max

# a linear range controller pretends the data spans a unit interval around the value
linear = qed.controllers.linearRange(name="constant_linear")
# tuning does not raise
linear.autotune(stats=zeros)
# the picks are distinct and bracket the value
assert linear.low < 0.0 < linear.high
assert linear.high - linear.low == 1.0
# and the bounds enclose the picks with room to move
assert linear.min < linear.low and linear.high < linear.max
# the same holds away from zero
linear.autotune(stats=(3.0, 3.0, 3.0))
assert linear.low < 3.0 < linear.high
assert linear.min < linear.low and linear.high < linear.max

# an all-zero raster, the way a user would meet one: a 65x65 complex file of nothing
scratch = pyre.primitives.path(tempfile.mkdtemp(prefix="qed_constant_"))
# the fixture
fixture = scratch / "zeros.dat"
# c16 cells are sixteen bytes each
fixture.open(mode="wb").write(bytes(65 * 65 * 16))
# open it
dataset = qed.readers.native.datasets.mmap(
    name="zeros", uri=f"file:{fixture}", cell="c16", shape=(65, 65)
)
# measure it, the way the blocking open path does; this used to divide by zero
stats = dataset.measure()
# the probe reports what it found
assert stats == zeros
# and every channel can render a tile of it
for name in dataset.channels:
    # get the pipeline
    pipeline = dataset.channel(name=name)
    # render
    tile = dataset.render(channel=pipeline, zoom=(0, 0), origin=(0, 0), shape=(64, 64))
    # and check that a bitmap came back
    assert len(bytes(memoryview(tile))) > 0
# clean up
fixture.unlink()
scratch.rmdir()


# end of file
