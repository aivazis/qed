# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# my interface
from .Node import Node


# a controller that captures a single value
class ValueController(graphene.ObjectType):
    """
    A controller that captures a single value
    """


    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = Node,

    # my fields
    id = graphene.ID()
    uuid = graphene.ID()
    # payload
    slot = graphene.String()
    min = graphene.Float()
    max = graphene.Float()
    value = graphene.Float()


# end of file
