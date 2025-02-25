# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload to turn a pair of anchors into a box
class ViewMeasureMakeBoxInput(graphene.InputObjectType):
    """
    The payload to turn the first two anchors of the measure path into a box
    """

    # the viewport
    viewport = graphene.Int(required=True)


# end of file
