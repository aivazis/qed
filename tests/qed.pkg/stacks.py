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


# a lightweight stand-in for a stack, carrying just what {_resolveMask} reads
def stackStandin(names, membership):
    """
    Build a minimal stand-in for a stack with the given member {names} and {membership}
    """
    # each member needs only its name for the mask resolution
    readers = [types.SimpleNamespace(pyre_name=name) for name in names]
    # hand back an object with the attributes {_resolveMask} reads
    return types.SimpleNamespace(readers=readers, membership=membership)


# check that the default participation mask is resolved correctly from the membership trait
def membershipMask():
    """
    Exercise {Stack._resolveMask}: empty means all, names select positionally, order is preserved
    """
    # the resolver, borrowed from the stack class
    resolve = qed.stacks.stack._resolveMask
    # an empty membership turns every member on
    assert resolve(stackStandin(["a", "b", "c"], [])) == [True, True, True]
    # a named subset turns on exactly those members
    assert resolve(stackStandin(["a", "b", "c"], ["a", "c"])) == [True, False, True]
    # the mask follows member order, not the order the names were listed in
    assert resolve(stackStandin(["a", "b", "c"], ["c", "a"])) == [True, False, True]
    # a membership that matches nothing falls back to the whole stack
    assert resolve(stackStandin(["a", "b"], ["x", "y"])) == [True, True]
    # all done
    return


# check that an aggregate dataset renders over only the participating members
def subsetRender():
    """
    Exercise {Dataset.render}: a mask reduces the members handed to the channel; absence means all
    """
    # build an aggregate over three members; pyre keys components by name, so this needs a name
    # all its own to avoid colliding with the dataset {test} builds above
    members = [member(), member(), member()]
    # the dataset under test
    dataset = qed.stacks.dataset(
        name="test.stack.subset.L.A.HH", members=members, selector={"band": "L"}
    )
    # a fake channel that records the members it is asked to reduce
    seen = {}

    def tile(source, datatype, zoom, origin, shape, members, **kwds):
        # remember what arrived
        seen["members"] = members
        # the result is irrelevant to this check
        return None

    channel = types.SimpleNamespace(tile=tile)
    # render with a mask that drops the middle member
    dataset.render(
        channel=channel, zoom=(0, 0), origin=(0, 0), shape=(8, 8), mask=[True, False, True]
    )
    # the channel must see exactly the first and third members, in order
    assert seen["members"] == [members[0], members[2]]
    # render without a mask, the channel reduces over every member
    dataset.render(channel=channel, zoom=(0, 0), origin=(0, 0), shape=(8, 8))
    # so it sees the full membership
    assert seen["members"] == members
    # all done
    return


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

    # check that the membership trait resolves into a sensible default mask
    membershipMask()
    # check that a mask reduces the members an aggregate dataset renders over
    subsetRender()

    # all done
    return 0


# bootstrap
if __name__ == "__main__":
    # invoke the driver
    status = test()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
