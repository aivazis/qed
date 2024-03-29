# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from ..DatasetMeasure import DatasetMeasure


# remove a view from the pile
class ToggleMeasureLayer(graphene.Mutation):
    """
    Toggle the state of the measure layer of a dataset
    """

    # inputs
    class Arguments:
        # the update context
        dataset = graphene.String(required=True)

    # the result is the new measure layer object
    measure = graphene.Field(DatasetMeasure)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, dataset):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it for the measure layer of the dataset view
        measure = store.datasetView(name=dataset).measure
        # toggle measure layer state
        measure.active ^= True
        # form the mutation resolution context
        context = {"measure": measure}
        # and resolve the mutation
        return context


# end of file
