#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the app
class Tiler(qed.cache.crew, family="qed.apps.tiler"):
    """
    A worker that fetches data tiles from h5 datasets in S3
    """


# bootstrap
if __name__ == "__main__":
    # instantiate
    app = Tiler(name="tiler")
    # invoke
    status = app.run()
    # and share
    raise SystemExit(status)


# end of file
