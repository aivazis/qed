# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# support
import qed

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
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.ID()
    uri = graphene.String()
    api = graphene.String()
    selectors = graphene.List(Selectors)
    datasets = graphene.List(Dataset)

    # the resolvers
    def resolve_id(reader, *_):
        """
        Get the {reader} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{reader.pyre_family()}:{reader.pyre_name}"

    def resolve_name(reader, *_):
        """
        Get the {reader} name
        """
        # return the {pyre_id} of the {reader}
        return reader.pyre_name

    def resolve_uri(reader, *_):
        """
        Get the path to the file
        """
        # resolve the uri
        return str(reader.uri)

    def resolve_api(reader, *_):
        """
        Get the entry point for data requests
        """
        # requests are resolved against {data}
        return "data"

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
