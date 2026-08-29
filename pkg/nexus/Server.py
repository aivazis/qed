# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import json

# support
import pyre

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

    # protocol obligations
    @pyre.export(tip="register this service with the nexus")
    def activate(self, app, dispatcher):
        """
        Register with the nexus and wire my fleet into the shared event loop
        """
        # chain up to grab a port and build the event hub
        super().activate(app=app, dispatcher=dispatcher)
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
            # the data sources stay passive: the server boots without touching any data
            # files, and first contact waits for a client to declare the catalog relevant
            # through the {stage} mutation
        # attach the fleet
        self.fleet = fleet
        # all done
        return

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


# end of file
