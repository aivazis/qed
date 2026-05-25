# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the shared interface for all controller types
class Controller(graphene.Interface):
    """
    The shared interface for all viz pipeline controller types
    """

    # shared fields
    id = graphene.ID()
    dirty = graphene.Boolean()
    slot = graphene.String()
    min = graphene.Float()
    max = graphene.Float()

    # type resolver
    @classmethod
    def resolve_type(cls, context, info):
        """
        Deduce the controller type from the {context} information
        """
        # avoid a circular import
        from .RangeController import RangeController
        from .ValueController import ValueController
        # the resolver table
        registry = {
            "range": RangeController,
            "value": ValueController,
        }
        # extract the type tag and look up the concrete type
        return registry[context["controller"].tag]


# end of file
