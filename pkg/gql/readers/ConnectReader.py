# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal
import qed

# the request payload
from .ConnectReaderInput import ConnectReaderInput

# the result types
from .Reader import Reader


# add a new data reader to the pile
class ConnectReader(graphene.Mutation):
    """
    Connect a new data reader
    """

    # inputs
    class Arguments:
        # the request payload
        input = ConnectReaderInput(required=True)

    # the result is always a reader
    reader = graphene.Field(Reader)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Add a new reader to the pile
        """
        # get the store
        store = info.context["store"]
        # unpack
        archive = input["archive"]
        reader = input["reader"]
        name = input["name"]
        uri = input["uri"]
        lines = input["lines"]
        samples = input["samples"]
        cell = input["cell"]
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
        # carefully, since the configuration may be malformed
        try:
            # instantiate; construction is passive, so this touches no file
            source = factory(archive=archive, **args)
        # if the reader cannot even be built
        except Exception as error:
            # make a channel
            channel = journal.error("qed.gql.connect")
            # complain
            channel.line(f"could not connect '{uri}'")
            channel.line(f"while building a '{reader}' instance")
            channel.line(f"got: {error}")
            # flush
            channel.log()
            # and report the failure as a mutation error, so the client's error handler
            # runs; returning a trivial reader used to look like success and poisoned the
            # client's catalog with a null
            raise
        # add the new source to the store
        store.connectSource(source=source)
        # connecting is the user asking for this product, so first contact starts now; it
        # happens on the product's crew, and this call returns while the survey runs, with
        # the outcome arriving over the event stream as {ready} or {failed}
        store.stage(name=source.pyre_name)
        # make a resolution context
        context = {"reader": source}
        # and resolve the mutation
        return context


# end of file
