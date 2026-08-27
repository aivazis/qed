#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that controllers widen their display bounds to accommodate accumulated statistics
without ever touching the user's picks, the dirty flag, or pinned configurations
"""

# support
import qed


# a log range controller, tuned to a modest sample: values around 1
log = qed.controllers.logRange(name="widen_log")
# tune it
log.autotune(stats=(0.9, 1.0, 1.1))
# remember its state
low, high = log.low, log.high
# and mark it clean, the way view registration does
log.dirty = False

# a sample whose bounds the controller already accommodates
assert log.widen(stats=(0.5, 1.0, 2.0)) is False
# moves nothing
assert log.low == low and log.high == high and log.dirty is False

# a sample with a large peak, e.g. a pole caught by a whole-dataset pass
assert log.widen(stats=(0.5, 1.3, 2654.0)) is True
# stretches the top to the next decade above the peak
assert log.max == 4
# leaves the picks alone
assert log.low == low and log.high == high
# and survives without marking the controller dirty
assert log.dirty is False

# a pinned controller
pinned = qed.controllers.logRange(name="widen_pinned")
# opts out of automatic adjustments
pinned.auto = False
# remember its bounds
bounds = (pinned.min, pinned.max)
# even an escaping sample
assert pinned.widen(stats=(1e-8, 1.0, 1e8)) is False
# moves nothing
assert (pinned.min, pinned.max) == bounds

# a linear range controller
linear = qed.controllers.linearRange(name="widen_linear")
# tuned to a narrow sample
linear.autotune(stats=(-1.0, 0.0, 1.0))
# and marked clean
linear.dirty = False
# remember its bounds
lo, hi = linear.min, linear.max
# a small escape within the slack
assert linear.widen(stats=(lo - 0.01, 0.0, hi + 0.01)) is False
# is tolerated
assert linear.min == lo and linear.max == hi
# a real escape
assert linear.widen(stats=(lo, 0.0, 10 * hi)) is True
# stretches the top past the data
assert linear.max > 10 * hi
# leaves the bottom alone
assert linear.min == lo
# and does not mark the controller dirty
assert linear.dirty is False


# end of file
