#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


"""
Check that we can load view persistent state
"""


# support
import qed

# load the app
app = qed.shells.qed(name="qed.app")
# build its dispatcher
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)


# end of file
