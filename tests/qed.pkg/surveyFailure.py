#! /usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a survey that cannot make first contact names the kind of failure in its report

The reason a survey failed is all the user ever sees of it, and the text of some errors is
meaningless on its own, e.g. a missing key whose entire message is its name; so the report
must carry the type of the error along with what it said
"""

# externals
import pickle

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# get the passive reader, before anybody has touched its file
reader, *_ = ux.store.sources
# describe its product as a survey task
task = qed.nexus.survey(reader=reader)
# point the recipe at a product that is not there
task.config["uri"] = "file:///nowhere/c16.dat"
# push it through the wire, the way the team marshals it to a crew member
task = pickle.loads(pickle.dumps(task))

# carefully, since first contact is expected to fail
try:
    # execute it the way a worker does, with a fresh reader registry
    task.execute(readers={})
# the failure must be the kind that leaves the crew member healthy
except task.RecoverableError as error:
    # get the reason
    reason = str(error)
    # it names the kind of failure
    assert reason.startswith("FileNotFoundError: ")
    # and retains what the error said
    assert "/nowhere/c16.dat" in reason
# if the survey went through
else:
    # it made contact with a product that does not exist
    assert False, "the survey of a missing product succeeded"


# end of file
