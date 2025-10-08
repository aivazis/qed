# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# information about a data collection
class DataCollectionInput(graphene.InputObjectType):
    """
    Information about a data collection
    """

    # the fields
    shortName = graphene.String(required=True)
    conceptId = graphene.String(required=True)


# end of file
