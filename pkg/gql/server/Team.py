# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a team of worker processes
class Team(graphene.ObjectType):
    """
    A team of worker processes: whom it works for, its roster, and its schedule
    """

    # its name
    name = graphene.String(required=True)
    # its kind: tile, build, or scout
    kind = graphene.String(required=True)
    # the reader, or the archive, it works for
    owner = graphene.String(required=True)
    # its size, and the members that are idle and busy
    size = graphene.Int(required=True)
    idle = graphene.Int(required=True)
    active = graphene.Int(required=True)
    # the tasks in its workplan, and the ones handed out and not yet back
    queued = graphene.Int(required=True)
    pending = graphene.Int(required=True)
    # the members nobody is listening to, and the ones about to be handed a task
    deaf = graphene.Int(required=True)
    waking = graphene.Int(required=True)


# end of file
