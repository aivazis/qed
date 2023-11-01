# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene
import journal
import qed

# the result types
from .Reader import Reader


# add a new data reader to the pile
class ConnectReader(graphene.Mutation):
    """
    Connect a new data reader
    """

    # inputs
    class Arguments:
        # the update context
        reader = graphene.String(required=True)
        name = graphene.String(required=True)
        uri = graphene.String(required=True)

    # the result is always a reader
    reader = graphene.Field(Reader)

    # the range controller mutator
    def mutate(root, info, reader, name, uri):
        """
        Add a new reader to the pile
        """
        # resolve the {reader} into a factory
        factory = qed.protocols.reader.pyre_resolveSpecification(spec=reader)
        # instantiate
        source = factory(name=name, uri=uri)
        # get the panel
        panel = info.context["panel"]
        # add the new source to the panel
        panel.readers[uri] = source
        # now, go through its datasets
        for dataset in source.datasets:
            # and add each one to the dataset registry
            panel.datasets[dataset.pyre_name] = dataset
        # make a resolution context
        context = {"reader": source}
        # and resolve the mutation
        return context


# end of file
