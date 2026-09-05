#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a missing extension is named rather than tripped over: the kernels of a product
raise an error whose message quotes the loader, and the server declines to come up
"""

# externals
import os

# support
import journal
import qed

# the error is one of ours
assert issubclass(qed.exceptions.ExtensionError, qed.exceptions.QEDError)

# the NISAR fixture; part of the shared test data tree
product = os.path.join(os.path.dirname(__file__), "..", "data", "nisar", "gslc.h5")
# if it has not been generated
if not os.path.exists(product):
    # there is nothing more to check
    raise SystemExit(0)

# a reader over it
reader = qed.readers.nisar.gslc(name="ext_gslc", uri=product)
# make first contact
reader.open()
# and grab a dataset
dataset, *_ = reader.datasets
# with the extension in place, the kernels are there
assert dataset.kernels is not None

# take the extension away, the way a failed import leaves things: the package and its
# extension module both point at nothing, and the reason is on record
libqed, reason = qed.libqed, qed.ext.libqed_error
qed.libqed = qed.ext.libqed = None
qed.ext.libqed_error = "undefined symbol: planted"
# carefully
try:
    # the kernels name the condition, quoting the loader and naming the product
    try:
        # ask
        dataset.kernels
    # the answer is an error of ours, not the absence of the property
    except qed.exceptions.ExtensionError as error:
        # with a message complete on its own
        assert "undefined symbol: planted" in str(error)
        assert "ext_gslc" in str(error)
    # anything else is a failure
    else:
        # complain
        assert False, "a missing extension went unnoticed"

    # the server declines to come up; its error channel is fatal by default
    server = qed.nexus.server(name="ext_server")
    # attempt to
    try:
        # activate it; the refusal comes before any port is bound
        server.activate(app=None, dispatcher=None)
    # the refusal is an application error
    except journal.ApplicationError:
        # as expected
        pass
    # anything else is a failure
    else:
        # complain
        assert False, "a server without its extension came up"
    # and nothing was built
    assert server.fleet is None
# whatever happens
finally:
    # restore the extension
    qed.libqed = qed.ext.libqed = libqed
    qed.ext.libqed_error = reason

# with the extension back, the kernels are there again
assert dataset.kernels is not None


# end of file
