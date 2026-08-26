#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a team survives the death of a crew member mid-task: the task's callback gets the
bad news, and a replacement is recruited
"""

# externals
import os

# support
import pyre
import qed


# a task that kills its worker
class Boom(pyre.nexus.task):
    """
    A task whose execution takes down the crew member abruptly, report unsent
    """

    # interface
    def execute(self, **kwds):
        """
        The body of the functor
        """
        # die without a trace
        os._exit(1)


# a well behaved task
class Echo(pyre.nexus.task):
    """
    A task with a recognizable result
    """

    # interface
    def execute(self, **kwds):
        """
        The body of the functor
        """
        # hand back a marker
        return "echo"


# build a team
team = qed.nexus.team(name="qed.test.casualty")
# with a single crew member, so the casualty is the member that must be replaced
team.size = 1
# the outcome drop box
outcomes = []


# the delivery callback
def deliver(result, error):
    """
    Record the outcome and stop the event loop
    """
    # file the report
    outcomes.append((result, error))
    # and wind down
    team.dispatcher.stop()
    # all done
    return


# queue the lethal task
team.assign(task=Boom(), callback=deliver)
# spin the event loop until the outcome is delivered
team.dispatcher.watch()

# unpack the outcome
result, error = outcomes[0]
# the task produced nothing
assert result is None
# and the failure was reported
assert error is not None

# now queue a normal task; the replacement crew member should handle it
team.assign(task=Echo(), callback=deliver)
# spin again
team.dispatcher.watch()

# unpack the second outcome
result, error = outcomes[1]
# this one succeeded
assert error is None
# with the expected result
assert result == "echo"

# send everybody home
team.disband()


# end of file
