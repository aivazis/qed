# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal
import qed

# my input type
from .ReaderInput import ReaderInput

# the result types
from .Reader import Reader


# add a new data reader to the pile
class ConnectReader(graphene.Mutation):
    """
    Connect a new data reader
    """

    # inputs
    class Arguments:
        spec = ReaderInput(required=True)

    # the result is always a reader
    reader = graphene.Field(Reader)

    # the range controller mutator
    def mutate(root, info, spec):
        """
        Add a new reader to the pile
        """
        # unpack
        reader = spec["reader"]
        name = spec["name"]
        uri = spec["uri"]
        lines = spec["lines"]
        samples = spec["samples"]
        cell = spec["cell"]
        # form the factory arguments
        args = {
            "name": name,
            "uri": uri,
        }
        # if there is a shape spec
        if lines and samples:
            # add it to the pile
            args["shape"] = (lines, samples)
        # if there is a data type spec
        if cell:
            # add it to the pile
            args["cell"] = cell

        # make a channel
        channel = journal.info("qed.gql.connect")
        channel.line(f"{reader=}")
        channel.line(f"{name=}")
        channel.line(f"{uri=}")
        channel.line(f"{lines=}, {samples=}")
        channel.line(f"{cell=}")
        channel.log()

        # resolve the {reader} into a factory
        factory = qed.protocols.reader.pyre_resolveSpecification(spec=reader)
        channel.log(f"{factory=}")
        # instantiate
        source = factory(**args)
        channel.log(f"{source=}")
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
