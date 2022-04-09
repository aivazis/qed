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
        types = ValueController, RangeController


# end of file
