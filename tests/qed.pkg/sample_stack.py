#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a stack samples a tile over all of its members

Each member samples the tile on its own, and the stack folds their records together; the
result has to be the record of all their cells taken at once, and a member whose tile holds
nothing has to leave it alone
"""

# externals
import math
import types

# support
import qed


def record(values):
    """
    The mergeable record of {values}, worked out the long way
    """
    # an empty tile
    if not values:
        # has the empty record
        return 0.0, 0.0, 0.0, 0.0, 0.0
    # the count
    count = len(values)
    # the mean
    mean = sum(values) / count
    # and the second moment about it
    m2 = sum((v - mean) ** 2 for v in values)
    # assemble the record
    return float(count), min(values), mean, m2, max(values)


def member(values):
    """
    Build a stand-in member whose tile holds {values}
    """
    # hand back an object with what a stack borrows from its members, and a sample
    return types.SimpleNamespace(
        # the in-memory layout
        datatype=qed.h5.memtypes.complex64,
        # the cell type; {None} is the dataset default
        cell=None,
        # a small extent
        shape=(8, 8),
        # the natural origin
        origin=(0, 0),
        # a tile that fits
        tile=(8, 8),
        # a positive (low, mean, high) sample, as the autotuners expect
        stats=(0.1, 1.0, 10.0),
        # the record of the tile, whichever tile is asked for
        sample=lambda zoom, origin, shape: record(values),
    )


def test():
    """
    Fold the samples of three members, one of them empty, and compare with the long way
    """
    # the cells of the members
    cells = [[1.0, 2.0, 7.5], [], [0.5, 3.25, 4.0, 9.0]]
    # make the stack; pyre keys components by name, so it needs one
    stack = qed.stacks.dataset(
        name="test.stack.sample.L.A.HH", members=[member(c) for c in cells], selector={}
    )
    # sample it
    combined = stack.sample(zoom=(0, 0), origin=(0, 0), shape=(8, 8))
    # the record of every cell at once
    reference = record([value for values in cells for value in values])
    # the two agree
    assert all(math.isclose(a, b, rel_tol=1e-12) for a, b in zip(combined, reference)), combined
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
