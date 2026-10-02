# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# support
import pyre
import qed

# my parts
from .Build import Build
from .ConfiguredComponent import ConfiguredComponent
from .Fleet import Fleet
from .ServerProcess import ServerProcess
from .ServerRequests import ServerRequests
from .TileCache import TileCache
from .Workspace import Workspace


# the server
class Server(graphene.ObjectType):
    """
    What the server is doing, one subsystem at a time
    """

    # the process, unless the server cannot describe it
    process = graphene.Field(ServerProcess)
    # the tile requests
    requests = graphene.Field(ServerRequests, required=True)
    # the cache of rendered tiles and the teams of workers, unless there is no fleet
    cache = graphene.Field(TileCache)
    fleet = graphene.Field(Fleet)
    # the preparation of every dataset a client has asked about
    builds = graphene.List(graphene.NonNull(Build), required=True)
    # the workspace, unless the application has none that can describe itself
    workspace = graphene.Field(Workspace)
    # the configuration of every component reachable from the application
    configuration = graphene.List(graphene.NonNull(ConfiguredComponent), required=True)

    # resolvers
    @staticmethod
    def resolve_process(store, info, **kwds):
        """
        Describe the process of the server
        """
        # the http server that took the request
        server = info.context["server"]
        # knows how to describe its process, if it is the qed server
        describe = getattr(server, "describe", None)
        # so ask it, if it can
        return describe() if describe is not None else None

    @staticmethod
    def resolve_requests(store, info, **kwds):
        """
        Describe the tile requests
        """
        # the dispatcher keeps track of them
        return info.context["dispatcher"].describe()

    @staticmethod
    def resolve_cache(store, info, **kwds):
        """
        Describe the cache of rendered tiles
        """
        # the fleet owns the cache
        fleet = store.fleet
        # so ask it, if there is one
        return fleet.cache.describe() if fleet is not None else None

    @staticmethod
    def resolve_fleet(store, info, **kwds):
        """
        Describe the teams of workers
        """
        # the store knows the fleet
        fleet = store.fleet
        # which describes its teams, if there is one
        return {"teams": fleet.describe()} if fleet is not None else None

    @staticmethod
    def resolve_workspace(store, info, **kwds):
        """
        Describe the workspace
        """
        # the application owns it
        workspace = info.context["plexus"].workspace
        # and it describes itself, if it knows how
        describe = getattr(workspace, "describe", None)
        # so ask it, if it can
        return describe() if describe is not None else None

    @staticmethod
    def resolve_configuration(store, info, **kwds):
        """
        Describe the configuration of every component reachable from the application: through
        its traits, and through the state the server keeps outside of them, e.g. the data
        sources in the store and the teams in the fleet
        """
        # the application
        plexus = info.context["plexus"]
        # the fleet, if the server has one
        fleet = getattr(info.context["server"], "fleet", None)
        # the roots of the walk: the application and the nexus it runs on
        roots = [plexus, getattr(plexus, "nexus", None)]
        # the fleet, its cache, and its teams
        if fleet is not None:
            roots.extend([fleet, fleet.cache, *fleet.teams.values()])
            roots.extend([*fleet.builds.values(), *fleet.explorers.values()])
        # the data sources, the archives, and the views in the store
        roots.extend([*store.sources, *store.archives])
        roots.extend(port.view() for port in store.viewports)
        # walk from the ones that are components
        return qed.ux.configuration(
            roots=[root for root in roots if isinstance(root, pyre.component)]
        )

    @staticmethod
    def resolve_builds(store, info, **kwds):
        """
        Describe the preparation of every dataset a client has asked about
        """
        # the store keeps the records
        return store.builds()


# end of file
