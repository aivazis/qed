# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# my fields
from .Selector import Selector


# my node type
class Dataset(graphene.ObjectType):
    """
    A dataset
    """

    # my fields
    id = graphene.ID()
    uuid = graphene.ID()
    selector = graphene.List(Selector)
    datatype = graphene.String()
    shape = graphene.List(graphene.Int)
    channels = graphene.List(graphene.String)


    # resolvers
    def resolve_id(dataset, *_):
        """
        Get the {dataset} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{dataset.pyre_family()}:{dataset.pyre_name}"


    def resolve_uuid(dataset, *_):
        """
        Get the {dataset} uuid
        """
        # return the {pyre_id} of the {reader}
        return dataset.pyre_id


    def resolve_selector(dataset, *_):
        """
        Flatten the selector
        """
        return dataset.selector.items()


    def resolve_datatype(dataset, *_):
        """
        Extract the payload data type identifier
        """
        # return the {family} name of the datatype marker
        return dataset.cell.pyre_family()


    def resolve_channels(dataset, *_):
        """
        Extract the payload data type identifier
        """
        # return the {family} name of the datatype marker
        return dataset.cell.channels


# end of file
