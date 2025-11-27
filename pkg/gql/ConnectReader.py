# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


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
    @staticmethod
    def mutate(root, info, spec):
        """
        Add a new reader to the pile
        """
        # get the store
        store = info.context["store"]
        # unpack
        archive = spec["archive"]
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
        # resolve the {reader} into a factory
        factory = qed.protocols.reader.pyre_resolveSpecification(spec=reader)
        # get the archive
        archive = store.archive(uri=archive)
        # instantiate
        source = factory(archive=archive, **args)
        # get the store
        store = info.context["store"]
        # add the new source to the store
        store.connectSource(source=source)
        # make a resolution context
        context = {"reader": source}
        # and resolve the mutation
        return context


# end of file
