#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the stacks package: the aggregate channels and the dataset that serves them
"""


# externals
import types

# support
import qed

# the aggregate channels live with the nisar product channels, for now
from qed.readers.nisar.products import channels


# a lightweight stand-in for a member dataset, carrying just what a stack dataset borrows
def member():
    """
    Build a minimal stand-in for a stack member dataset
    """
    # hand back an object with the attributes a stack dataset reads from its members
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
    )


# the driver
def test():
    """
    Check that a stack exposes its aggregate channels, named so the view can find them
    """
    # the package publishes the stack factory and its aggregate dataset
    assert qed.stacks.stack is not None
    assert qed.stacks.dataset is not None

    # the two aggregate channels are published with the tags and category the system keys on
    assert channels.meanpower.tag == "meanpower"
    assert channels.meanpower.category == "stack"
    assert channels.stackCoherence.tag == "coherence"
    assert channels.stackCoherence.category == "stack"

    # build an aggregate dataset over a couple of stand-in members
    dataset = qed.stacks.dataset(
        name="test.stack.L.A.HH", members=[member(), member()], selector={"band": "L"}
    )
    # it must offer exactly the two aggregate channels, keyed by tag
    assert set(dataset.channels) == {"meanpower", "coherence"}
    # and each pipeline must be named after its tag, so {view.setChannel} can look it up; this
    # guards against the regression where a channel was named by its module key instead
    for tag, pipeline in dataset.channels.items():
        # the registry key the view builds is "{view}.{dataset}.{tag}"
        assert pipeline.pyre_name == f"{dataset.pyre_name}.{tag}"

    # all done
    return 0


# bootstrap
if __name__ == "__main__":
    # invoke the driver
    status = test()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
