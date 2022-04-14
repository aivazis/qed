# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# base types
from .RangeController import RangeController
from .ValueController import ValueController


# the union of all controller types
class Controller(graphene.Union):
    """
    The union of all controller types
    """


    # metadata
    class Meta:
        # my possible types
        types = RangeController, ValueController


    # the type resolver
    @classmethod
    def resolve_type(cls, instance, info):
       """
       Deduce the controller type from the {instance} information
       """
       # extract the type
       controller = instance.controller
       # look up the associated class in my registryand return it
       return cls.registry[controller]


    # the resolver table
    registry = {
        "range": RangeController,
        "value": ValueController,
    }


# end of file
