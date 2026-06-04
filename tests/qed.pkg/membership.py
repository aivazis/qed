#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the per-member participation logic a view carries for a stack reader
"""


# externals
import types

# support
import qed


# check the translation from a participation mask to the list of active member indices
def activeMembers():
    """
    Exercise {View._activeMembers}: the on positions, in member order; nothing when there is no mask
    """
    # the accessor, borrowed from the view class
    active = qed.ux.view._activeMembers
    # no mask, e.g. the reader is not a stack, means no active members
    assert active(types.SimpleNamespace(members=None)) == []
    # an empty mask likewise
    assert active(types.SimpleNamespace(members=[])) == []
    # a mixed mask reports the on positions in order
    assert active(types.SimpleNamespace(members=[True, False, True])) == [0, 2]
    # an all-on mask reports every position
    assert active(types.SimpleNamespace(members=[True, True, True])) == [0, 1, 2]
    # all done
    return


# check the guards and effect of setting a participation mask
def setMembers():
    """
    Exercise {View.setMembers}: the empty set is rejected; a real mask is stored and re-resolved
    """
    # the mutator, borrowed from the view class
    setter = qed.ux.view.setMembers

    # turning every member off would empty the stack, so it is rejected
    calls = []
    standin = types.SimpleNamespace(members=[True, True], resolve=lambda: calls.append(1))
    # ask to turn everyone off
    setter(standin, members=[False, False])
    # the mask is left untouched
    assert standin.members == [True, True]
    # and the view does not re-resolve
    assert calls == []

    # a non-empty mask is accepted, stored, and triggers a re-resolution
    standin = types.SimpleNamespace(members=[True, False], resolve=lambda: calls.append(1))
    # ask to turn the second member back on
    setter(standin, members=[True, True])
    # the new mask is stored
    assert standin.members == [True, True]
    # and the view re-resolves exactly once
    assert calls == [1]

    # all done
    return


# the driver
def test():
    """
    Check the view's participation-mask helpers in isolation
    """
    # the mask-to-indices translation
    activeMembers()
    # the mask mutator and its empty-set guard
    setMembers()
    # all done
    return 0


# bootstrap
if __name__ == "__main__":
    # invoke the driver
    status = test()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
