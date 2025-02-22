# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my fields
from .Channel import Channel
from .Selector import Selector


# my node type
class Dataset(graphene.ObjectType):
    """
    A dataset
    """

    # my fields
    id = graphene.ID()
    name = graphene.ID()

    channels = graphene.List(Channel)
    datatype = graphene.String()
    selector = graphene.List(Selector)
    shape = graphene.List(graphene.Int)
    origin = graphene.List(graphene.Int)
    tile = graphene.List(graphene.Int)

    # resolvers
    @staticmethod
    def resolve_id(dataset, *_):
        """
        Get the {dataset} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{dataset.pyre_family()}:{dataset.pyre_name}"

    @staticmethod
    def resolve_name(dataset, *_):
        """
        Get the name of the dataset
        """
        # easy enough
        return dataset.pyre_name

    @staticmethod
    def resolve_channels(dataset, *_):
        """
        Extract the names of supported channels
        """
        # return the names of available channels
        return dataset.channels.values()

    @staticmethod
    def resolve_datatype(dataset, *_):
        """
        Extract the payload data type identifier
        """
        # return the {family} name of the datatype marker
        return dataset.cell.pyre_family()

    @staticmethod
    def resolve_selector(dataset, *_):
        """
        Flatten the selector
        """
        return dataset.selector.items()


# end of file
