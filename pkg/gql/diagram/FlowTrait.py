# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a trait of a factory, as the inspector shows it
class FlowTrait(graphene.ObjectType):
    """
    A trait of a factory: one of its input or output slots, or one of its settings
    """

    # the fields
    # the name of the trait
    name = graphene.String(required=True)
    # what it is to the factory: "input", "output", or "setting"
    kind = graphene.String(required=True)
    # its type
    type = graphene.String(required=True)
    # its current value, rendered as text
    value = graphene.String()
    # its default, rendered as text
    default = graphene.String()
    # its documentation
    doc = graphene.String()


# end of file
