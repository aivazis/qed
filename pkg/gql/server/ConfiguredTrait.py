# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the configuration of one trait
class ConfiguredTrait(graphene.ObjectType):
    """
    A trait of a component: its value, where the value came from, and the components it refers
    to; the value of a secret trait is not reported
    """

    # the name of the trait
    name = graphene.String(required=True)
    # its kind: property or facility
    kind = graphene.String(required=True)
    # its type
    schema = graphene.String(required=True)
    # its value, rendered as a string, missing when it is secret or has none
    value = graphene.String()
    # whether it is secret
    secret = graphene.Boolean(required=True)
    # the category of the source of its value, e.g. defaults, user, or command
    priority = graphene.String()
    # where exactly the value came from
    locator = graphene.String()
    # the components the value refers to
    components = graphene.List(graphene.NonNull(graphene.String), required=True)


# end of file
