#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a crew member that dies or misbehaves before checking in gets buried instead of
crashing the event loop or leaking in the registration roster
"""

# externals
import os

# support
import pyre
import qed

# build a team
team = qed.nexus.team(name="qed.test.stillborn")
# of a single member
team.size = 1


# manufacture a member whose worker died before its registration arrived
def stillborn():
    """
    Build a team side proxy whose worker end closed without a word
    """
    # make a child that dies immediately, so there is a real corpse to reap
    pid = os.fork()
    # in the child
    if pid == 0:
        # die on the spot
        os._exit(1)
    # make the channel
    parent, child = pyre.ipc.newSocket().open()
    # the worker end closes without ever writing the registration
    child.close()
    # build the team side proxy
    crew = qed.nexus.crew(pid=pid, channel=parent)
    # wire it the way the recruiter does
    crew.dispatcher = team.dispatcher
    crew.marshaler = team.marshaler
    # and hand it off
    return crew


# scenario 1: the registration never arrives
crew = stillborn()
# enroll the member the way {join} does
team.registered.add(crew)
# fire the registration handler; it finds a closed channel
keep = crew.activate(channel=crew.channel, team=team)
# the handler winds down quietly
assert keep is False
# the member was buried and a replacement recruited on the spot
survivors = list(team.crews())
assert crew not in survivors
assert len(survivors) == 1
# and the corpse was reaped
try:
    # so a second wait
    os.waitpid(crew.pid, 0)
    # must not find it
    assert False
# because it was already collected
except ChildProcessError:
    # as expected
    pass


# scenario 2: the registration arrives but does not vouch for a healthy member
pid = os.fork()
# in the child
if pid == 0:
    # die on the spot
    os._exit(1)
# make the channel
parent, child = pyre.ipc.newSocket().open()
# the worker end sends garbage instead of a clean bill of health
team.marshaler.send(item="garbage", channel=child)
# and closes
child.close()
# build the team side proxy
crew = qed.nexus.crew(pid=pid, channel=parent)
# wire it
crew.dispatcher = team.dispatcher
crew.marshaler = team.marshaler
# enroll it
team.registered.add(crew)
# fire the registration handler; it finds a compromised member
keep = crew.activate(channel=parent, team=team)
# the handler winds down quietly
assert keep is False
# and the member was buried, with a replacement recruited on the spot
survivors = list(team.crews())
assert crew not in survivors
assert len(survivors) == 1

# send everybody home
team.disband()


# end of file
