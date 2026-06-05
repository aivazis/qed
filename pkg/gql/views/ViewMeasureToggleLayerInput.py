# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to toggle a reader's participation in the measure layer
class ViewMeasureToggleLayerInput(graphene.InputObjectType):
    """
    The payload to toggle a reader's participation in the measure layer
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the reader
    reader = graphene.String(required=True)


# end of file
