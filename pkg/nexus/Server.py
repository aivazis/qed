# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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
        # attach the fleet
        self.fleet = fleet
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


# end of file
