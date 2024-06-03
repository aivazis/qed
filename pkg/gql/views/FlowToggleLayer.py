# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .Flow import Flow


# remove a view from the pile
class FlowToggleLayer(graphene.Mutation):
    """
    Toggle the state of the flow layer of a dataset
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)
        reader = graphene.String(required=True)

    # the result is the new flow layer object
    flow = graphene.Field(Flow)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, reader):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it for the flow layer of the dataset view
        flow = store.toggleFlow(viewport=viewport, source=reader)
        # form the mutation resolution context
        context = {"flow": flow}
        # and resolve the mutation
        return context


# end of file
