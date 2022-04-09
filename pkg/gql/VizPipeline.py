# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# individual controls
from .Controller import Controller


# a representation of the visualization pipeline for a specific {channel} of a {dataset}
class VizPipeline(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    dataset = graphene.ID()
    channel = graphene.ID()
    controllers = graphene.List(Controller)


    # resolvers
    def resolve_dataset(context, info, **kwds):
        """
        Extract the name of the dataset
        """
        # get the dataset
        dataset = context["dataset"]
        # and return its name
        return dataset.pyre_name


# end of file
