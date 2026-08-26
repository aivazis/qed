# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# the teams i manage
from .Team import Team

# the cache of rendered tiles they share
from .Cache import Cache


# the manager of the tile rendering teams
class Fleet(qed.component, family="qed.nexus.fleets.tile"):
    """
    The manager of the tile rendering teams, one per data source

    Crew members open their own copy of the data product they render, so dedicating a team to
    each product keeps every worker's caches hot for exactly one product, isolates the request
    queues of slow products from snappy ones, and lets a product's resources be released when
    it is disconnected
    """

    # interface
    def lookup(self, task):
        """
        Retrieve the cached render of {task}, if it is on hand
        """
        # consult the cache
        return self.cache.lookup(task=task)

    def render(self, task, callback):
        """
        Route {task} to the team dedicated to its data source and arrange for {callback} to
        receive the outcome
        """
        # locate the team, building it on first contact
        team = self.team(reader=task.reader)
        # and hand it the work
        team.assign(task=task, callback=callback)
        # all done
        return self

    def team(self, reader):
        """
        Retrieve the team dedicated to {reader}, building it on first contact
        """
        # look it up
        team = self.teams.get(reader)
        # if it exists
        if team is not None:
            # hand it off
            return team
        # build the team; its name places its configuration under my namespace, so users can
        # adjust individual team sizes, e.g. '{fleet}.{reader}.size'; the fleet itself grows
        # with the loaded data products, so total worker load is the user's call
        team = Team(name=f"{self.pyre_name}.{reader}")
        # the team's crew traffic rides the shared event loop
        team.dispatcher = self.dispatcher
        # and its successful renders land in the shared cache
        team.cache = self.cache
        # register it
        self.teams[reader] = team
        # show me
        channel = journal.debug("qed.nexus.fleet")
        # what happened
        channel.log(f"formed a team of {team.size} for '{reader}'")
        # and hand it off
        return team

    def revoke(self, task, callback):
        """
        Withdraw {callback} from the outcome of {task}, e.g. because its requester hung up
        """
        # find the team responsible for the task's data source
        team = self.teams.get(task.reader)
        # if it exists
        if team is not None:
            # pass the word
            team.revoke(task=task, callback=callback)
        # all done
        return self

    def dismiss(self, reader):
        """
        Disband the team dedicated to {reader}, e.g. because its data source was disconnected
        """
        # look up the team, removing it from my registry
        team = self.teams.pop(reader, None)
        # if there is one
        if team is not None:
            # send its crews home
            team.disband()
        # and drop the departed product's renders from the cache
        self.cache.purge(reader=reader)
        # all done
        return self

    def disband(self):
        """
        Disband all my teams
        """
        # go through my teams
        for team in self.teams.values():
            # and send each one's crews home
            team.disband()
        # empty the registry
        self.teams.clear()
        # and release every cached render
        self.cache.clear()
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the table of teams, keyed by the name of their data source
        self.teams = {}
        # the cache of rendered tiles, shared by all of them; its name places its
        # configuration under my namespace, e.g. '{fleet}.cache.capacity'
        self.cache = Cache(name=f"{self.pyre_name}.cache")
        # the shared event loop; whoever builds me is responsible for setting it before any
        # tiles are rendered
        self.dispatcher = None
        # all done
        return


# end of file
