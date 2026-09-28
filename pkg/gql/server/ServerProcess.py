# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the process of the server
class ServerProcess(graphene.ObjectType):
    """
    The process of the server: what it is, where it runs, how long it has been up, and the
    descriptors it holds against its ceiling
    """

    # the process id
    pid = graphene.Int(required=True)
    # the host and the platform
    host = graphene.String(required=True)
    platform = graphene.String(required=True)
    # the cores and the memory of the host, in bytes
    cores = graphene.Int(required=True)
    memory = graphene.Float(required=True)
    # when the server came up, in seconds since the epoch, and for how long it has been up
    started = graphene.Float()
    uptime = graphene.Float(required=True)
    # the descriptors it holds, unknown on a platform that cannot tell, and its ceiling
    descriptors = graphene.Int()
    ceiling = graphene.Int(required=True)
    # the heartbeats so far
    beats = graphene.Int(required=True)


# end of file
