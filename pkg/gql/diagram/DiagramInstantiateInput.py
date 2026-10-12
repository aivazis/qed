# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to pin a factory of the pipeline diagram to a new instance
class DiagramInstantiateInput(graphene.InputObjectType):
    """
    The payload to pin a factory of the pipeline diagram to a new instance of a class: the one
    named, or the one the factory is pinned to, under a name a person may give it
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the id of the factory
    node = graphene.ID(required=True)
    # the family of the class to make an instance of; none means the one the factory is pinned to
    family = graphene.String()
    # the name of the new instance; none, or empty, leaves it unnamed
    name = graphene.String()


# end of file
