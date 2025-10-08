# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# information about a data granule
class DataGranuleInput(graphene.InputObjectType):
    """
    Information about a data granule
    """

    # the fields
    pattern = graphene.String(required=True)


# end of file
