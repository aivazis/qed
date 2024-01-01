# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .Reader import Reader


# remove a data reader from the pile
class DisconnectReader(graphene.Mutation):
    """
    Disconnect a data reader
    """

    # inputs
    class Arguments:
        # the update context
        uri = graphene.String(required=True)

    # the result is the disconnected reader
    reader = graphene.Field(Reader)

    # the range controller mutator
    def mutate(root, info, uri):
        """
        Remove a reader from the pile
        """
        # get the panel
        panel = info.context["panel"]
        # resolve the reader
        reader = panel.readers[uri]
        # remove it from the pile
        del panel.readers[uri]
        # go through its datasets
        for dataset in reader.datasets:
            # and remove each one from the dataset registry
            del panel.datasets[dataset.pyre_name]
        # form the mutation resolution context
        context = {"reader": reader}
        # and resolve the mutation
        return context


# end of file
