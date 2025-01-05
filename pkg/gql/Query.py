# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import importlib

# support
import qed
import journal

# types
from .Item import Item
from .Metadata import Metadata
from .QED import QED
from .Sample import Sample
from .Shape import Shape
from .Version import Version


# the query
class Query(graphene.ObjectType):
    """
    The top level query
    """

    # the known queries
    # server version info
    version = graphene.Field(Version, required=True)
    # the session manager
    qed = graphene.Field(QED)
    # directory contents
    contents = graphene.List(
        Item, required=True, archive=graphene.String(), path=graphene.String()
    )
    # dataset auto discovery
    discover = graphene.Field(
        Metadata,
        archive=graphene.String(),
        uri=graphene.String(),
        module=graphene.String(),
    )
    # samples
    sample = graphene.Field(
        Sample, dataset=graphene.ID(), sample=graphene.Int(), line=graphene.Int()
    )
    # generation of shape guesses from a raster size
    guessShape = graphene.Field(
        graphene.List(Shape), size=graphene.String(), aspect=graphene.String()
    )

    # the resolvers
    # the session manager
    @staticmethod
    def resolve_qed(root, info, **kwds):
        """
        Get the session layout
        """
        # grab the store
        store = info.context["store"]
        # and pass it on
        return store

    # directory contents
    @staticmethod
    def resolve_contents(root, info, archive, path, **kwds):
        """
        Generate a list with the contents of a directory
        """
        # this resolver must exist; its job is to build an object that gets handed to the
        # {Item} resolvers; here we prep such an object using the query execution
        # context in {info.context} and the variable bindings in {kwds}
        #
        #     root: should be {None}; this is the root
        #     info: has {.context} with whatever was built by the executioner
        #     kwds: contains the variable bindings for this query resolution
        #

        # grab the store
        store = info.context["store"]
        # identify the archive
        manager = store.archive(uri=archive)
        # attempt to
        try:
            # ask it for its contents
            return manager.contents(uri=qed.primitives.uri.parse(path))
        # if anything goes wrong
        except journal.ApplicationError:
            # swallow
            pass
        # all done
        return []

    # product metadata
    @staticmethod
    def resolve_discover(root, info, archive, uri, module, **kwds):
        """
        Generate a list with the contents of a directory
        """
        # assemble the metadata resolution context
        context = {
            "archive": archive,
            "uri": uri,
            "module": module,
            "metadata": None,
        }
        # make a channel
        channel = journal.info("qed.gsl.discover")
        # show me
        channel.line(f"retrieving metadata for '{uri}'")
        channel.indent()
        channel.line(f"archive: {archive}")
        channel.line(f"module: {module}")
        channel.outdent()
        # flush
        channel.log()
        # attempt to
        try:
            # get the metadata factory
            factory = importlib.import_module(module).metadata
        # if twe have a bad module
        except ImportError as error:
            # make a channel
            channel = journal.error("qed.gql.discover")
            # complain
            channel.line(f"'{module}' not found")
            channel.indent()
            channel.line(f"{error}")
            channel.line(f"while attempting to discover metadata")
            channel.line(f"for dataset '{uri}'")
            channel.line(f"in archive '{archive}'")
            channel.outdent()
            # flush
            channel.log()
            # bail
            return context
        # if the module doesn't support metadata discover
        except AttributeError as error:
            # make a channel
            channel = journal.error("qed.gql.discover")
            # complain
            channel.line(f"'{module}' does not support metadata discovery")
            channel.indent()
            channel.line(f"{error}")
            channel.line(f"while attempting to discover metadata")
            channel.line(f"for dataset '{uri}'")
            channel.line(f"in archive '{archive}'")
            channel.outdent()
            # flush
            channel.log()
            # bail
            return context
        # attempt to
        try:
            # load the metadata
            metadata = factory(uri=uri)
        # if anything goes wrong
        except Exception as error:
            # make a channel
            channel = journal.error("qed.gql.discover")
            # complain
            channel.line(f"'{module}' does not recognize this file")
            channel.indent()
            channel.line(f"{error}")
            channel.line(f"while attempting to discover metadata")
            channel.line(f"for dataset '{uri}'")
            channel.line(f"in archive '{archive}'")
            channel.outdent()
            # flush
            channel.log()
            # bail
            return context

        # show me
        channel.line("metadata:")
        channel.indent()
        channel.line(f"uri: {metadata.uri}")
        channel.line(f"product: {metadata.product}")
        channel.line(f"description: {metadata.description}")
        channel.line(f"auxiliary file: {metadata.aux}")
        channel.line(f"size: {metadata.bytes}")
        channel.line(f"width: {metadata.width}")
        channel.line(f"height: {metadata.height}")
        channel.line(f"bands: {metadata.bands}")
        channel.line(f"interleaving: {metadata.interleaving}")
        channel.line(f"type: {metadata.type}")
        channel.line(f"endian: {metadata.endian}")
        channel.line(f"version: {metadata.version}")
        channel.line(f"spec: {metadata.spec}")
        channel.outdent()
        # flush
        channel.log()
        # if all goes well, attach the metadata to the context
        context["metadata"] = metadata
        # and hand it to the resolver
        return context

    # samples
    @staticmethod
    def resolve_sample(root, info, dataset, line, sample, **kwds):
        """
        Sample a dataset at a specified pixel
        """
        # grab the store
        store = info.context["store"]
        # resolve the dataset
        dataset = store.dataset(name=dataset)
        # assemble the sample resolution context
        context = {
            "dataset": dataset,
            "line": line,
            "sample": sample,
        }
        # and hand it to the sample resolver
        return context

    # the viz controls
    @staticmethod
    def resolve_viz(root, info, dataset, channel, **kwds):
        """
        Build a representation of the visualization controls
        """
        # get the store
        store = info.context["store"]
        # resolve the dataset
        dataset = store.dataset(name=dataset)
        # and the channel
        channel = dataset.channel(name=channel)
        # assemble the resolution context
        context = {
            "dataset": dataset,
            "channel": channel,
        }
        # and hand it to the resolver
        return context

    # shape guesses
    @staticmethod
    def resolve_guessShape(root, info, size, aspect, **kwds):
        """
        Generate a list of guess for the shape of a raster
        """
        # cast the inputs
        size = int(size)
        aspect = int(aspect)
        # factorize
        for lines, samples in qed.libqed.factor(product=size, aspect=aspect):
            # and build a guess
            yield {"lines": lines, "samples": samples}
        # all done
        return

    # version
    @staticmethod
    def resolve_version(root, info):
        """
        Build and return the server version
        """
        # supply the context for the {version} resolution
        return qed.meta


# end of file
