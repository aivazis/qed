# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import atexit
import functools
import os
import signal

# support
import pyre
import journal

# the unit of time
from pyre.units.SI import second

# the stock team; not re-exported by {pyre.nexus}, so reach into the package
from pyre.nexus.Pool import Pool

# my crew members
from .Crew import Crew

# my recruiter
from .Fork import Fork


# the tile rendering team
class Team(Pool, family="qed.nexus.teams.tile"):
    """
    A pool of persistent worker processes that render tiles

    Unlike the stock pool, which drafts workers per workplan and dismisses them when it
    drains, this team keeps its crew members around: idle ones are parked and woken when new
    tiles are requested; and task outcomes are delivered to per-task callbacks instead of
    being discarded
    """

    # types
    # my members render tiles
    crew = Crew
    # the marker for failures that the client can recover from by asking again
    from pyre.nexus.exceptions import RecoverableError

    # user configurable state
    size = pyre.properties.int(default=4)
    size.doc = "the number of crew members to recruit"

    recruiter = pyre.nexus.recruiter(default=Fork)
    recruiter.doc = "the strategy for recruiting crew members"

    # interface
    def render(self, task, callback):
        """
        Queue {task} for rendering and arrange for {callback} to receive the outcome
        """
        # a disbanded team renders nothing
        if self._disbanded:
            # so let the caller down right away
            callback(
                result=None, error=self.RecoverableError(description="team disbanded")
            )
            # all done
            return self
        # register the callback under the task
        self.pending[task] = callback
        # and add the task to the workplan
        self.assemble(workplan={task})
        # all done
        return self

    def collect(self, task, result):
        """
        A crew member has delivered the tile for {task}
        """
        # look up the callback
        callback = self.pending.pop(task, None)
        # a missing entry means the task outcome was already delivered; it's a bug
        if callback is None:
            # build a channel
            firewall = journal.firewall("qed.nexus.team")
            # complain
            firewall.line(f"duplicate delivery for {task}")
            firewall.line(f"while collecting a result in {self}")
            # flush
            firewall.log()
            # and bail, in case firewalls aren't fatal
            return self
        # hand the callback the tile
        callback(result=result, error=None)
        # all done
        return self

    def abandon(self, task, error):
        """
        A crew member could not render the tile for {task}
        """
        # look up the callback
        callback = self.pending.pop(task, None)
        # a missing entry means the task outcome was already delivered; it's a bug
        if callback is None:
            # build a channel
            firewall = journal.firewall("qed.nexus.team")
            # complain
            firewall.line(f"duplicate abandonment for {task}: {error}")
            firewall.line(f"while delivering bad news in {self}")
            # flush
            firewall.log()
            # and bail, in case firewalls aren't fatal
            return self
        # hand the callback the bad news
        callback(result=None, error=error)
        # all done
        return self

    def crews(self):
        """
        Generate every current crew member, whatever its state
        """
        # chain up for the ones checking in and the ones on a task
        yield from super().crews()
        # and add the ones parked on the bench
        yield from self.idle
        # all done
        return

    def bury(self, crew):
        """
        A {crew} member died without a formal dismissal; clean up after it and restore the
        team to full strength
        """
        # remove the member from all rosters
        self.registered.discard(crew)
        self.active.discard(crew)
        self.idle.discard(crew)
        self.vigils.discard(crew)
        # carefully
        try:
            # close the team side of its channel
            crew.channel.close()
        # tolerating one that is already gone
        except OSError:
            # nothing further
            pass
        # carefully
        try:
            # reap the corpse
            os.waitpid(crew.pid, 0)
        # tolerating one that was already collected
        except (OSError, ChildProcessError):
            # nothing further
            pass
        # recruiting a replacement right away would let the descriptor just freed be reused
        # and re-registered within the dispatch cycle that closed it, before the event loop
        # has purged the dead registration; defer the recovery to a fresh cycle
        self.dispatcher.alarm(interval=0 * second, call=self.recover)
        # all done
        return self

    def recover(self, timestamp):
        """
        Restore the team to full strength after a casualty
        """
        # a disbanded team stays disbanded; a recovery that was pending when the team was
        # sent home must not resurrect it
        if self._disbanded:
            # so it does nothing
            return None
        # otherwise, recruit replacements and wake the bench, in case there is work waiting
        self.assemble(workplan=set())
        # do not reschedule this alarm
        return None

    def disband(self):
        """
        Dismiss every crew member; invoked at shutdown so no workers are orphaned
        """
        # crew dismissal is a team side activity; forked children that inherited my atexit
        # registration must not attempt it
        if os.getpid() != self._manager:
            # so they bail
            return self
        # mark me, so a recovery that was pending at this moment cannot resurrect me
        self._disbanded = True
        # the parked and still-checking-in members are between tasks and exit on request
        resting = set(self.idle) | set(self.registered)
        # members that are mid-task would block writing a report nobody will drain, so a
        # graceful dismissal can deadlock the exit; they get terminated instead
        working = set(self.active)
        # empty the rosters
        self.idle.clear()
        self.active.clear()
        self.registered.clear()
        self.vigils.clear()
        # go through the resting members
        for crew in resting:
            # carefully, since a member may have died on its own
            try:
                # ask each one to exit
                crew.dismissed()
                # and reap the process
                self.recruiter.dismiss(team=self, crew=crew)
            # dead members raise while being messaged or waited on
            except (OSError, ChildProcessError):
                # nothing more to do for them
                continue
        # go through the working members
        for crew in working:
            # carefully, for the same reason
            try:
                # terminate each one; its render is moot at exit
                os.kill(crew.pid, signal.SIGKILL)
                # and reap the process
                os.waitpid(crew.pid, 0)
            # dead members raise while being signaled or waited on
            except (OSError, ChildProcessError):
                # nothing more to do for them
                continue
        # tasks still awaiting outcomes will never get one; deliver the bad news so parked
        # requests are answered rather than left hanging
        for task, callback in list(self.pending.items()):
            # let each one down gently
            callback(
                result=None, error=self.RecoverableError(description="team disbanded")
            )
        # and clear the ledger
        self.pending.clear()
        # all done
        return self

    # team protocol obligations
    @pyre.export
    def assemble(self, workplan, **kwds):
        """
        Add the tasks in {workplan} to my schedule
        """
        # extend the workplan
        self.workplan |= workplan
        # recruit up to full strength
        self.recruit()
        # if there is work to do
        if self.workplan:
            # wake the parked crew members; extras just go back to the bench
            while self.idle:
                # take each one off the bench
                crew = self.idle.pop()
                # return it to duty
                self.active.add(crew)
                # and put it back on the schedule
                self.schedule(crew=crew)
        # all done
        return self

    @pyre.export
    def vacancies(self):
        """
        Compute how many recruits are needed to take the team to full strength
        """
        # my crew members are persistent, so aim for full strength regardless of backlog;
        # everybody counts: the ones checking in, the ones on a task, and the parked ones
        return self.size - len(self.registered) - len(self.active) - len(self.idle)

    # implementation details
    def submit(self, channel, crew, **kwds):
        """
        A crew member has reported ready to accept tasks
        """
        # if there is nothing to do at the moment
        if not self.workplan:
            # take the crew member off duty
            self.active.discard(crew)
            # and park it; a future {assemble} will wake it
            self.idle.add(crew)
            # keep an eye on the parked member, so its death gets noticed and its channel
            # stays visible to the event loop; the watch survives wake/repark rounds, since
            # it only clears when its handler fires, so arm at most one per member: a member
            # that was woken but found no work still has its old watch standing
            if crew not in self.vigils:
                # mark it
                self.vigils.add(crew)
                # and arm the watch
                self.dispatcher.whenReadReady(
                    channel=crew.channel, call=functools.partial(self.vigil, crew=crew)
                )
            # and don't reschedule this handler
            return False
        # otherwise, grab a task
        task = self.workplan.pop()
        # carefully, since the member may have died while waiting for work
        try:
            # send it off
            crew.execute(team=self, task=task)
        # if its channel is broken
        except OSError:
            # the task was never attempted, so put it back for somebody else
            self.workplan.add(task)
            # and clean up after the member; the replacement will pick the task up
            self.bury(crew=crew)
        # the harvesting of the result decides the fate of this crew member
        return False

    def vigil(self, channel, crew, **kwds):
        """
        The channel of a parked {crew} member has activity

        A parked member has nothing to say, so the only possibility is that it died and its
        end of the channel closed; but if the member has been woken since this watch was set,
        the activity is a task report and belongs to the harvesting handler
        """
        # this watch is spent, whatever happens next; a future park may arm a fresh one
        self.vigils.discard(crew)
        # if the member is no longer parked
        if crew not in self.idle:
            # this watch is stale; drop it without touching the channel
            return False
        # otherwise, the member is gone; clean up after it
        self.bury(crew=crew)
        # and drop the watch
        return False

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the bench of parked crew members
        self.idle = set()
        # the members with an armed death watch
        self.vigils = set()
        # the callbacks awaiting task outcomes, keyed by task
        self.pending = {}
        # remember which process manages the team, so forked members can tell they are not it
        self._manager = os.getpid()
        # the marker that i have been sent home for good
        self._disbanded = False
        # the server exits by raising {SystemExit} from deep inside the event loop, which
        # bypasses the orderly service shutdown; register the cleanup so crews never outlive me
        atexit.register(self.disband)
        # all done
        return


# end of file
