# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .ConfiguredTrait import ConfiguredTrait


# the configuration of one component
class ConfiguredComponent(graphene.ObjectType):
    """
    A component reachable from the application, and the configuration of its traits
    """

    # the name of the component
    name = graphene.String(required=True)
    # its family, if it has one
    family = graphene.String()
    # its traits
    traits = graphene.List(graphene.NonNull(ConfiguredTrait), required=True)


# end of file
