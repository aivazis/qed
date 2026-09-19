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

A failed attempt must also leave no trace: the worker that tried once rebuilds the reader
under the same name, which hands back the same instance, so a reader that considered itself
opened after a failure would let the next survey through with nothing to show for it
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

# the registry of open readers of the worker; it outlives any one task
readers = {}
# a survey that fails gets asked for again, and the request may well land on the same worker
for attempt in range(3):
    # carefully, since first contact is expected to fail
    try:
        # execute it the way a worker does
        task.execute(readers=readers)
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
        assert False, f"attempt {attempt}: the survey of a missing product succeeded"
    # a reader that could not be opened is not among the open readers of the worker
    assert readers == {}


# end of file
