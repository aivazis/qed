#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the whole-dataset statistics accumulator merges per-tile records exactly: folding
partial records in any order must agree with a single pass over all the values
"""

# externals
import statistics

# support
import qed


# reduce a batch of values to the record a worker would ship
def record(values):
    """
    Build the mergeable (count, min, mean, m2, max) record of {values}
    """
    # the population size
    count = len(values)
    # the mean
    mean = statistics.fmean(values)
    # the second moment about the mean
    m2 = sum((v - mean) ** 2 for v in values)
    # assemble the record
    return (count, min(values), mean, m2, max(values))


# two batches of values, deliberately lopsided
first = [1.0, 2.0, 3.0, 4.0]
second = [10.0, 20.0, 30.0]

# an accumulator
sample = qed.ux.sample()
# fold in the two partial records
sample.merge(record=record(first))
sample.merge(record=record(second))

# the reference: a single pass over the union
count, low, mean, m2, high = record(first + second)
# the population size matches
assert sample.count == count
# so do the extrema
assert sample.min == low and sample.max == high
# the mean agrees
assert abs(sample.mean - mean) < 1e-12
# and so does the second moment, hence the variance
assert abs(sample.m2 - m2) < 1e-9
assert abs(sample.variance - m2 / count) < 1e-9
# two records were folded in
assert sample.tiles == 2

# an empty record, e.g. from an all-nan tile
sample.merge(record=(0.0, 0.0, 0.0, 0.0, 0.0))
# contributes nothing
assert sample.count == count and sample.tiles == 2

# merge order must not matter: fold the batches the other way around
mirror = qed.ux.sample()
mirror.merge(record=record(second))
mirror.merge(record=record(first))
# and compare the running state
assert mirror.count == sample.count
assert mirror.min == sample.min and mirror.max == sample.max
assert abs(mirror.mean - sample.mean) < 1e-12
assert abs(mirror.m2 - sample.m2) < 1e-9


# end of file
