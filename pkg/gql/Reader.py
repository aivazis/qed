# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# my interface
from .Node import Node
# my parts
from .Dataset import Dataset
from .Selectors import Selectors


# my node type
class Reader(graphene.ObjectType):
    """
    A dataset reader
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = Node,

    # my fields
    id = graphene.ID()
    uuid = graphene.ID()
    uri = graphene.String()
    selectors = graphene.List(Selectors)
    datasets = graphene.List(Dataset)


    # the resolvers
    def resolve_id(reader, *_):
        """
        Get the {reader} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{reader.pyre_family()}:{reader.pyre_name}"


    def resolve_uuid(reader, *_):
        """
        Get the {reader} uuid
        """
        # return the {pyre_id} of the {reader}
        return reader.pyre_id


    def resolve_uri(reader, *_):
        """
        Get the path to the file
        """
        # turn the {uri} into an absolute path and send it off
        return reader.uri.resolve()


    def resolve_selectors(reader, *_):
        """
        Build a list of the selector names and their allowed values
        """
        return reader.selectors.items()


    def resolve_datasets(reader, *_):
        """
        Build a list of the available datasets
        """
        return reader.datasets


# end of file
