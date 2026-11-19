#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that controllers adopt hand-set display bounds only when the bounds leave the picks in
place, and that a hand-set extent pins the controller against automatic adjustments
"""

# support
import qed

# a linear range controller with a known configuration
linear = qed.controllers.linearRange(name="resize_linear")
# spread out
linear.min, linear.low, linear.high, linear.max = -10.0, -1.0, 1.0, 10.0
# and marked clean, the way view registration does
linear.dirty = False

# an inverted extent is refused
assert linear.resize(min=5.0, max=-5.0) is False
# so is a degenerate one
assert linear.resize(min=0.0, max=0.0) is False
# an extent that encroaches on the low pick
assert linear.resize(min=-0.5, max=10.0) is False
# or on the high pick
assert linear.resize(min=-10.0, max=0.5) is False
# each refusal leaves everything alone
assert (linear.min, linear.low, linear.high, linear.max) == (-10.0, -1.0, 1.0, 10.0)
# including the pin and the dirty flag
assert linear.auto is True
# and clean
assert linear.dirty is False

# an extent that fits snugly around the picks is accepted
assert linear.resize(min=-1.0, max=1.0) is True
# the bounds move
assert (linear.min, linear.max) == (-1.0, 1.0)
# the picks do not
assert (linear.low, linear.high) == (-1.0, 1.0)
# the controller is now pinned
assert linear.auto is False
# and dirty, since the edit is worth persisting
assert linear.dirty is True

# once pinned, statistics can no longer stretch the bounds
assert linear.widen(stats=(-100.0, 0.0, 100.0)) is False
# so they stay where they were
assert (linear.min, linear.max) == (-1.0, 1.0)
# nor can a fresh sample retune it
linear.autotune(stats=(-100.0, 0.0, 100.0))
# so it stays where it was
assert (linear.min, linear.low, linear.high, linear.max) == (-1.0, -1.0, 1.0, 1.0)

# a log range controller, in log scale
log = qed.controllers.logRange(name="resize_log")
# with a known configuration
log.min, log.low, log.high, log.max = -7.0, -6.0, 3.0, 4.0
# an extent that squeezes past the high pick is refused
assert log.resize(min=-7.0, max=2.0) is False
# so the extent stays where it was
assert (log.min, log.max) == (-7.0, 4.0)
# a wider one is adopted and pins the controller
assert log.resize(min=-8.0, max=8.0) is True
# so the extent moves
assert (log.min, log.max) == (-8.0, 8.0)
# and the controller is pinned
assert log.auto is False
# so an escaping sample no longer moves it
assert log.widen(stats=(1e-12, 1.0, 1e12)) is False
# so the extent stays where it was
assert (log.min, log.max) == (-8.0, 8.0)

# a value controller
value = qed.controllers.value(name="resize_value")
# with a known configuration
value.min, value.value, value.max = 0.0, 0.5, 1.0
# an extent that leaves the pick outside is refused, from either side
assert value.resize(min=0.6, max=1.0) is False
# and from the other
assert value.resize(min=0.0, max=0.4) is False
# so the controller stays where it was
assert (value.min, value.value, value.max) == (0.0, 0.5, 1.0)
# an extent that just reaches the pick is fine
assert value.resize(min=0.5, max=2.0) is True
# so the extent moves, and the pick stays
assert (value.min, value.value, value.max) == (0.5, 0.5, 2.0)
# and pins the controller
assert value.auto is False

# a pinned controller can be released
value.unpin()
# which lets statistics move it again
assert value.auto is True
# but a value controller is not scaled by the data, so statistics never stretch it
bounds = (value.min, value.max)
# so releasing it with statistics on offer does not move it
assert value.unpin(stats=(-1.0, 0.5, 3.0)) is False
# and its bounds stay where they were
assert (value.min, value.max) == bounds
# a pin is a pin, with or without an edit
value.pin()
# so it is pinned
assert value.auto is False

# releasing a range controller with statistics on offer stretches the bounds right away
assert linear.unpin(stats=(-100.0, 0.0, 100.0)) is True
# to accommodate the data, with the usual breathing room
assert linear.auto is True
# past the extremes of the data
assert linear.min < -100.0 and linear.max > 100.0
# without touching the picks
assert (linear.low, linear.high) == (-1.0, 1.0)
# and a release with nothing to catch up on leaves the bounds alone
bounds = (linear.min, linear.max)
# has nothing to report
assert linear.unpin() is False
# and the bounds stay where they were
assert (linear.min, linear.max) == bounds

# the checks are available without committing to a move
assert value.accommodates(min=0.0, max=1.0) is True
# while one that leaves the pick outside does not
assert value.accommodates(min=0.6, max=1.0) is False
# and neither does an empty one
assert value.accommodates(min=1.0, max=1.0) is False


# end of file
