# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# my interface
from .Node import Node


# a controller that captures a range of values
class AmplitudeController(graphene.ObjectType):
    """
    A controller that captures a range of values
    """


    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = Node,

    # my fields
    # id
    id = graphene.ID()
    uuid = graphene.ID()
    # payload
    slot = graphene.String()
    min = graphene.Float()
    max = graphene.Float()
    low = graphene.Float()
    high = graphene.Float()


# end of file
