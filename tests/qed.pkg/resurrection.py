#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a disbanded team stays disbanded: pending recoveries do not resurrect it, and new
work is refused immediately
"""

# support
import pyre
import qed


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
team = qed.nexus.team(name="qed.test.resurrection")
# with a single crew member
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


# queue a task and spin until it is delivered
team.assign(task=Echo(), callback=deliver)
team.dispatcher.watch()
# the task succeeded
assert outcomes[0] == ("echo", None)

# send everybody home
team.disband()
# nobody is left
assert list(team.crews()) == []

# a recovery arriving after disband must not resurrect the team
team.recover()
# still nobody
assert list(team.crews()) == []

# and new work is refused on the spot
team.assign(task=Echo(), callback=deliver)
# with the bad news delivered synchronously
result, error = outcomes[1]
assert result is None
assert error is not None
# and no crews were recruited for it
assert list(team.crews()) == []


# end of file
