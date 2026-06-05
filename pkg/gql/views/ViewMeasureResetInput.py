# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to reset the measure state back to its persisted value
class ViewMeasureResetInput(graphene.InputObjectType):
    """
    The payload to reset the measure state back to its persisted value
    """

    # the viewport
    viewport = graphene.Int(required=True)


# end of file
