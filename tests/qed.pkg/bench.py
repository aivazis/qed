#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the death of a parked crew member is noticed: the watch buries it and a
replacement is recruited
"""

# externals
import os
import signal

# support
import pyre
import qed

# the unit of time
from pyre.units.SI import second


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


# the alarm that winds down the event loop
def expire(timestamp):
    """
    Stop the event loop
    """
    # ask the dispatcher to stop
    team.dispatcher.stop()
    # and don't reschedule
    return None


# build a team
team = qed.nexus.team(name="qed.test.bench")
# with a single crew member
team.size = 1
# the outcome drop box
outcomes = []


# the delivery callback
def deliver(result, error):
    """
    Record the outcome
    """
    # file the report; leave the loop running so the crew member gets parked
    outcomes.append((result, error))
    # all done
    return


# queue a task
team.render(task=Echo(), callback=deliver)
# let the loop run long enough for the member to render and get parked
team.dispatcher.alarm(interval=1 * second, call=expire)
# spin
team.dispatcher.watch()

# the task was delivered
assert outcomes and outcomes[0] == ("echo", None)
# and the member is parked
assert len(team.idle) == 1

# get the parked member
(crew,) = team.idle
# and kill it behind the team's back
os.kill(crew.pid, signal.SIGKILL)

# let the loop notice
team.dispatcher.alarm(interval=1 * second, call=expire)
# spin
team.dispatcher.watch()

# the casualty was buried
assert crew not in set(team.crews())
# and a replacement took its place, so the team is back at full strength
assert len(list(team.crews())) == 1

# send everybody home
team.disband()


# end of file
