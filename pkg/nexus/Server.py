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

    descriptors = pyre.properties.int(default=None)
    descriptors.doc = "the descriptor ceiling to ask for at startup; left unset, as many as the system allows"

    history = pyre.properties.int(default=2048)
    history.doc = (
        "how many journal records to keep for clients that open the console late"
    )

    latency = pyre.properties.dimensional(default=0.1 * second)
    latency.doc = (
        "how long journal records accumulate before going out to clients as a batch"
    )

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
        # ask for as many descriptors as the system allows, before anything that holds them
        # is built: every cached tile, every crew channel, and every client connection is
        # one, and a shell's default ceiling is a few hundred
        self._widen()
        # from here on, everything said to the journal also reaches the browser: install the
        # device that records and publishes entries, with the terminal as its mirror, before
        # the fleet is built, so the crews inherit it and their replayed entries land on it
        self._listen()
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
    def _listen(self):
        """
        Install the journal device that keeps a history and publishes entries to live clients
        """
        # the device that reaches the browser; imported here to keep the ux package out of
        # this module's dependencies until it is needed
        from ..ux.Journal import Journal

        # the device the journal has been writing to, typically the terminal
        terminal = journal.chronicler.device
        # build mine, with the terminal as its mirror
        self.journal = Journal(
            server=self, mirror=terminal, capacity=self.history, latency=self.latency
        )
        # and make it the default device
        journal.chronicler.device = self.journal
        # all done
        return

    def _widen(self) -> int:
        """
        Raise the ceiling on the descriptors this process may hold, as far as the system
        allows, and report where it landed

        Whatever ceiling this process starts with is inherited by every crew member it forks,
        so this happens once, before the fleet is built
        """
        # where things stand
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        # the ceilings worth asking for, highest first: the one the user named, the hard
        # limit when it is a number, and the usual system caps when it is not
        wanted = [self.descriptors] if self.descriptors is not None else []
        wanted += [hard] if hard != resource.RLIM_INFINITY else []
        wanted += [65536, 10240, 4096, 1024]
        # go through them
        for ceiling in wanted:
            # a ceiling no higher than the current one is not worth asking for
            if ceiling <= soft:
                # so stop looking
                break
            # carefully, since the system may refuse
            try:
                # ask
                resource.setrlimit(resource.RLIMIT_NOFILE, (ceiling, hard))
            # if it does
            except (ValueError, OSError):
                # try the next one
                continue
            # make a channel
            channel = journal.info("qed.nexus.server")
            # and say what happened, since a low ceiling is how tiles stop arriving
            channel.log(f"descriptor ceiling raised from {soft} to {ceiling}")
            # all done
            return ceiling
        # nothing was raised, so the current ceiling stands
        return soft

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
            # the zooms the tiles were asked at, which is what the pyramid is for
            zooms = ux.usage() if ux is not None else "no tiles yet"
            # hand back the whole picture
            return (
                f"fds={self._descriptors()} waiting={waiting} oldest={oldest:.1f}s "
                f"| cache: {cache} | zooms: {zooms} | {teams}"
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
        # if my journal device was installed
        if self.journal is not None:
            # give the journal back to the terminal
            journal.chronicler.device = self.journal.mirror
        # chain up
        return super().shutdown()

    # implementation details
    # private data
    fleet = None  # the manager of the tile rendering teams, built at activation
    journal = None  # the device that records and publishes journal entries, installed at activation
    _changeFrame = None  # the constant change notification frame, built on first use
    _app = (
        None  # the application, held so the heartbeat can describe what it is carrying
    )
    _beat = 0  # how many times the heartbeat has been raised


# end of file
