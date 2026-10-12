# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to change a setting of a factory of the pipeline diagram
class DiagramConfigureInput(graphene.InputObjectType):
    """
    The payload to change a setting of a factory of the pipeline diagram: a factory pinned to an
    instance has the setting changed, one pinned to a class is pinned to a new instance of it,
    under the given name, that carries the new value
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the id of the factory
    node = graphene.ID(required=True)
    # the name of the setting
    trait = graphene.String(required=True)
    # its new value, as text
    value = graphene.String(required=True)
    # the name of the instance to make, for a factory pinned to a class
    name = graphene.String()


# end of file
