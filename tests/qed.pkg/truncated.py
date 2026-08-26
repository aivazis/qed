#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that messages cut short mid-body are treated as a death, on both sides of the channel

A peer that dies mid-write leaves a header that promises more than the channel delivers; the
pickler trips over the stub with an unpickling error rather than the header unpacking error,
so this path is distinct from a channel that closed cleanly
"""

# externals
import os
import struct

# support
import pyre
import qed

# scenario 1: the worker side {perform} finds a truncated task
# make a channel
parent, child = pyre.ipc.newSocket().open()
# build a worker side member; nothing gets reaped here, so my own pid will do
worker = qed.nexus.crew(pid=os.getpid(), channel=child)
# hand-craft a message whose header promises far more than what follows
parent.write(bytes=struct.pack("<L", 100) + b"stub")
# and hang up
parent.close()
# fire the task handler; it finds the stub
keep = worker.perform(channel=child)
# and winds down quietly instead of raising
assert keep is False


# scenario 2: the team side {assess} finds a truncated report
# build a team
team = qed.nexus.team(name="qed.test.truncated")
# of a single member
team.size = 1
# make a child that dies immediately, so there is a real corpse to reap
pid = os.fork()
# in the child
if pid == 0:
    # die on the spot
    os._exit(1)
# make the channel
parent, child = pyre.ipc.newSocket().open()
# build the team side proxy
crew = qed.nexus.crew(pid=pid, channel=parent)
# wire it the way the recruiter does
crew.dispatcher = team.dispatcher
crew.marshaler = team.marshaler
# the member is mid-task
team.active.add(crew)
# with a task whose outcome somebody is waiting for
task = pyre.nexus.task()
# the outcome drop box
outcomes = []


# the delivery callback
def deliver(result, error):
    """
    Record the outcome
    """
    # file the report
    outcomes.append((result, error))
    # all done
    return


# register the callback
team.pending[task] = [deliver]
# the worker dies mid-report: a header, a fragment of the body, then nothing
child.write(bytes=struct.pack("<L", 64) + b"partial")
# and the channel closes
child.close()
# fire the harvesting handler; it finds the fragment
keep = crew.assess(channel=parent, team=team, task=task)
# the handler winds down quietly
assert keep is False
# the bad news was delivered
result, error = outcomes[0]
assert result is None
assert error is not None
# and the member was buried, with a replacement recruited on the spot
survivors = list(team.crews())
assert crew not in survivors
assert len(survivors) == 1

# send everybody home
team.disband()


# end of file
