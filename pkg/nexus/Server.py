# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import json
import os
import resource

# support
import pyre
import journal

# the unit the heartbeat period is expressed in
from pyre.units.SI import second

# the stock http server; its package does not re-export it, so reach in
from pyre.http.Server import Server as http

# the manager of the tile rendering teams
from .Fleet import Fleet


# the qed flavor of the http server
class Server(http, family="qed.nexus.servers.http"):
    """
    An http server that renders data tiles concurrently

    It owns a fleet of persistent worker teams, one per data source, that share the server's
    event loop; the connection parking that lets a response wait for its team is inherited
    from the stock server's deferred response machinery
    """

    # user configurable state
    period = pyre.properties.dimensional(default=1 * second)
    period.doc = "how often the heartbeat reports that the event loop is still turning"

    # protocol obligations
    @pyre.export(tip="register this service with the nexus")
    def activate(self, app, dispatcher):
        """
        Register with the nexus and wire my fleet into the shared event loop
        """
        # chain up to grab a port and build the event hub
        super().activate(app=app, dispatcher=dispatcher)
        # hold on to the application; it is the only thing in reach of everything the
        # heartbeat wants to report on
        self._app = app
        # start the heartbeat. it is the one instrument that tells a server whose loop has
        # died apart from one whose loop is turning while the work sits still: if the beats
        # stop, the loop is gone; if they keep coming while requests go unanswered, the loop
        # is fine and something downstream is not moving
        dispatcher.alarm(interval=self.period, call=self._heartbeat)
        # build my fleet of tile rendering teams; its name places its configuration under
        # mine, so users can adjust it, e.g. '{server}.fleet.capacity'
        fleet = Fleet(name=f"{self.pyre_name}.fleet")
        # its teams must never spin their own event loops: crew traffic is serviced by the
        # node's selector, so hand the fleet the shared dispatcher
        fleet.dispatcher = dispatcher
        # find the ux manager, mounted while the application folders were being assembled
        ux = getattr(app, "_ux", None)
        # if it is there
        if ux is not None:
            # the statistical samples the crews take drain into the store, where they
            # accumulate into whole-dataset statistics
            fleet.stats = ux.store.accumulate
            # and when the accumulation moves controller bounds, the store broadcasts a
            # change notification so live clients refetch their state
            ux.store.notifier = self.notifyChange
            # the store hands its sources to the fleet for first contact, so a survey
            # happens on a crew member rather than on this loop
            ux.store.fleet = fleet
            # and the crews are told where the application keeps what it derives, so the
            # levels they build land where this process will look for them
            ux.store.workspace = app.workspace
            # the data sources stay passive: the server boots without touching any data
            # files, and first contact waits for a client to declare the catalog relevant
            # through the {stage} mutation
        # attach the fleet
        self.fleet = fleet
        # all done
        return

    # implementation details
    def _heartbeat(self, timestamp, **kwds):
        """
        Report that the event loop is still turning, and what it is carrying

        N.B.: this is an alarm handler; whatever interval it returns is how long until it is
        raised again. It always asks to be raised, whatever the channel is doing, so that a
        missing beat means the loop and never the configuration
        """
        # count the beats, so a gap shows as a jump in the numbers rather than having to be
        # read out of timestamps
        self._beat += 1
        # make a channel
        channel = journal.debug("qed.nexus.heartbeat")
        # say how the loop is and what it is carrying
        channel.log(f"beat {self._beat}: {self._workload()}")
        # ask to be raised again
        return self.period

    def _descriptors(self) -> str:
        """
        Report how many file descriptors this process holds, against how many it may

        This is the number that turns a server which has stopped answering into a diagnosis
        rather than a mystery. Everything that serves a static asset or renders a tile needs
        a descriptor, so a count creeping up on the ceiling explains a freeze that no amount
        of staring at the tile path ever will -- while the one request that needs no
        descriptor, a graphql query against state already in memory, keeps answering and
        makes the server look healthy
        """
        # the ceiling is inherited from whichever shell launched the server, so ask rather
        # than assume the system default
        ceiling, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
        # carefully, since the count is a convenience and its absence must not cost the beat
        try:
            # every open descriptor appears here, on the platforms that have it; the listing
            # itself holds one while it runs, so this reads one high
            held = len(os.listdir("/dev/fd"))
        # a platform without it
        except OSError:
            # says nothing rather than guessing
            return f"?/{ceiling}"
        # otherwise, the count against the ceiling
        return f"{held}/{ceiling}"

    def _workload(self) -> str:
        """
        Describe what the server is carrying, in one line

        Two numbers matter while a freeze is being hunted: how many tile requests are parked
        waiting for an answer, and what each team's roster and queue look like. A loop that
        keeps beating while the first climbs and the second does not move is a loop that is
        fine and work that is not
        """
        # carefully, since this runs on a timer and must never be the thing that breaks
        try:
            # the ux manager owns the ledger of parked requests
            ux = getattr(self._app, "_ux", None)
            # ask it how many are waiting and how long the oldest has waited
            waiting, oldest = ux.backlog() if ux is not None else (0, 0.0)
            # the fleet owns the teams that do the work
            fleet = getattr(ux.store, "fleet", None) if ux is not None else None
            # describe each team that has been formed
            teams = (
                " | ".join(
                    f"{name}: {team.census()}" for name, team in fleet.teams.items()
                )
                if fleet is not None and fleet.teams
                else "no teams yet"
            )
            # the cache is what turns rendered tiles into held descriptors, so it reports
            # beside them
            cache = fleet.cache.census() if fleet is not None else "no cache"
            # hand back the whole picture
            return (
                f"fds={self._descriptors()} waiting={waiting} oldest={oldest:.1f}s "
                f"| cache: {cache} | {teams}"
            )
        # if anything at all goes wrong
        except Exception as error:
            # say so, rather than losing the beat that proves the loop is alive
            return f"workload unavailable: {error}"

    # interface
    def notifyChange(self):
        """
        Push a change notification to every live client subscribed to my hub
        """
        # the notification frame is constant, so build it once; the framing matches the one
        # the graphql handler broadcasts after successful mutations, so clients treat both
        # identically: any message means "refetch your state"
        if self._changeFrame is None:
            # use the {EventStream} framing so the wire format lives in one place
            stream = self.eventStream(server=self)
            # a minimal payload
            self._changeFrame = stream.event(json.dumps({"type": "change"}))
        # broadcast it on the global topic; coalesce, so a burst collapses into a single
        # pending refetch per client rather than a storm
        self.hub.publish(self._changeFrame, coalesce=True)
        # all done
        return

    @pyre.export(tip="shutdown")
    def shutdown(self):
        """
        Send the crews home and clean up
        """
        # if my fleet was ever assembled
        if self.fleet is not None:
            # disband it; the teams are also registered at exit, and disbanding is idempotent,
            # since the {stop} url exits by raising {SystemExit} without visiting the orderly
            # shutdown path
            self.fleet.disband()
        # chain up
        return super().shutdown()

    # implementation details
    # private data
    fleet = None  # the manager of the tile rendering teams, built at activation
    _changeFrame = None  # the constant change notification frame, built on first use
    _app = None  # the application, held so the heartbeat can describe what it is carrying
    _beat = 0  # how many times the heartbeat has been raised


# end of file
