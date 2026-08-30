#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the statistics probe finds data that a single center window misses

A geocoded product frames its data inside a much larger grid of fill, so the middle of the
raster is often empty; the NISAR fixture is built that way. Seeding the display range from
one window in the middle therefore measures nothing at all, and the kernel falls back to
nominal values. Probing a spread of windows across the extent costs about the same and
finds the data wherever it sits
"""

# support
import journal
import pyre
import qed

# the NISAR fixture this driver reads; part of the shared test data tree
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gslc.h5"
# if it has not been generated
if not product.exists():
    # there is nothing to check
    raise SystemExit(0)

# quiet the configuration chatter
journal.warning("qed.cli").deactivate()

# open the product without measuring it, so the datasets carry no statistics yet
reader = qed.readers.nisar.gslc(name="probed", uri=f"file:{product}")
reader.open(measure=False)
# take its first dataset
dataset, *_ = reader.datasets
# nobody has measured it
assert dataset.stats is None

# the extent, and the single center window the old seed used to look at
shape = tuple(dataset.shape)
window = tuple(min(256, axis) for axis in shape)
center = tuple((axis - side) // 2 for axis, side in zip(shape, window))
# that window holds nothing but fill: its mergeable record counts no cells at all, which
# is what made the seed a fabrication rather than a measurement
assert dataset.sample(zoom=(0, 0), origin=center, shape=window)[0] == 0

# the probe, on the other hand, finds the data
low, mean, high = qed.readers.probe(dataset=dataset)
# it reports a real range
assert high > low
# whose mean sits inside it
assert low <= mean <= high
# and which is not the nominal range the kernel invents when it finds nothing
assert (low, mean, high) != (0.0, 0.5, 1.0)

# measuring the dataset installs exactly that
dataset.measure()
assert dataset.stats == (low, mean, high)
# and tunes the channels against it; the amplitude range is the one the stretch reads
amplitude = dataset.channel(name="amplitude").amplitude
# so it must have moved off its configured default and onto the measured data
assert amplitude.low is not None
assert amplitude.high is not None

# a probe that finds nothing anywhere says so, and still yields a usable range: a linear
# channel cannot render without one, so the nominal values are a deliberate fallback rather
# than a measurement dressed up as one
empty = qed.readers.native.datasets.mmap(
    name="empty", hydrated=True, uri=f"file:{product}", cell="float32", shape=(4, 4)
)
# a hydrated twin holds no payload, so its sampler reports nothing for every window
empty.sample = lambda zoom, origin, shape: (0, 0.0, 0.0, 0.0, 0.0)
# the complaint is the point, so let it out where a human would see it, but not here
journal.warning("qed.readers.statistics").deactivate()
# probe it
assert qed.readers.probe(dataset=empty) == (0.0, 0.5, 1.0)


# end of file
