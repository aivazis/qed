# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the payload of the coordinate selection
class ViewSelectorInput(graphene.InputObjectType):
    """
    The payload for a selector toggle
    """

    # the fields
    viewport = graphene.Int()
    reader = graphene.String()
    selector = graphene.String()
    value = graphene.String()


# end of file
