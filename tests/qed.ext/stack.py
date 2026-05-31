#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the nisar stack tile-generator bindings are available
"""


# support
import qed


# the driver
def test():
    """
    The aggregate tile generators must be bound
    """
    # the stack submodule
    stack = qed.libqed.nisar.stack
    # the mean-power generator
    assert stack.meanpower is not None
    # and the coherence generator
    assert stack.coherence is not None
    # all done
    return 0


# bootstrap
if __name__ == "__main__":
    # invoke the driver
    status = test()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
