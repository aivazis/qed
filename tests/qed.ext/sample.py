#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the strided mergeable sample kernel: the Welford moments, the stride arithmetic,
the nan hygiene, and the magnitude reduction of complex sources
"""

# externals
import numpy as np

# support
import qed

# a 4x4 ramp
ramp = np.arange(16, dtype=np.float32).reshape(4, 4)
# sample every other cell in each direction: the values 0, 2, 8, 10
record = qed.libqed.native.sample(
    source=ramp, origin=(0, 0), shape=(2, 2), stride=(2, 2)
)
# four samples, from 0 to 10, with mean 5 and second moment 68
assert record == (4.0, 0.0, 5.0, 68.0, 10.0)

# an all-nan tile
fog = np.full((4, 4), np.nan, dtype=np.float32)
# contributes an empty record
record = qed.libqed.native.sample(
    source=fog, origin=(0, 0), shape=(2, 2), stride=(2, 2)
)
# with nothing in it
assert record == (0.0, 0.0, 0.0, 0.0, 0.0)

# a complex tile with magnitudes 5, 0, 0, 10
z = np.array([[3 + 4j, 0], [0, 6 + 8j]], dtype=np.complex64)
# is sampled by magnitude
record = qed.libqed.native.sample(source=z, origin=(0, 0), shape=(2, 2), stride=(1, 1))
# unpack
count, low, mean, m2, high = record
# four samples spanning 0 to 10
assert count == 4.0 and low == 0.0 and high == 10.0
# with mean 15/4
assert abs(mean - 3.75) < 1e-6
# and the matching second moment
assert abs(m2 - 68.75) < 1e-6

# a decimated origin is scaled by the stride: origin (1,1) at stride (2,2) starts at cell (2,2)
record = qed.libqed.native.sample(
    source=ramp, origin=(1, 1), shape=(1, 1), stride=(2, 2)
)
# so the single sample is the value at (2,2)
assert record == (1.0, 10.0, 10.0, 0.0, 10.0)


# end of file
