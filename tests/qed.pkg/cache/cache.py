#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the app
class Cache(qed.cache.bureau, family="qed.apps.cache"):
    """
    Exercise dataset caching
    """


# bootstrap
if __name__ == "__main__":
    # activate some channels
    # journal.debug("qed").activate()

    # instantiate
    app = Cache(name="cache")
    # invoke
    status = app.run()
    # and share
    raise SystemExit(status)

    # journal bug: look at the reported line numbers
    # channel = journal.debug("qed")
    # channel.log("what what?")
    # channel.log("what what?")
    # end of journal bug


# end of file
